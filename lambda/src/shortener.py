"""
Business logic: generate codes, interact with DynamoDB.
"""

import logging
import random
import string
import time
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from config import TABLE_NAME, CODE_LENGTH, DEFAULT_TTL_DAYS

logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

# Base62 alphabet: 0-9, A-Z, a-z — 62 chars
ALPHABET = string.digits + string.ascii_letters

# Collision retry limit
MAX_RETRIES = 5


def generate_code(length: int = CODE_LENGTH) -> str:
    """Return a random base62 code of the given length."""
    return "".join(random.choices(ALPHABET, k=length))


def create_short_url(original_url: str, custom_code: Optional[str] = None) -> dict:
    """
    Insert a new short URL. Retries on collision up to MAX_RETRIES.

    Returns the created item (code + original_url).
    Raises RuntimeError if all retries collide (astronomically unlikely).
    """
    now = int(time.time())
    expires_at = now + DEFAULT_TTL_DAYS * 86400 if DEFAULT_TTL_DAYS else None

    for attempt in range(MAX_RETRIES):
        code = custom_code or generate_code()
        item = {
            "code": code,
            "original_url": original_url,
            "created_at": now,
            "clicks": 0,
        }
        if expires_at:
            item["expires_at"] = expires_at

        try:
            # attribute_not_exists(code) = "fail if this PK already exists"
            # This is DynamoDB's conditional write — atomic, no race conditions.
            table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(code)",
            )
            logger.info("Created code=%s attempt=%d", code, attempt + 1)
            return item

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                if custom_code:
                    # User asked for a specific code and it's taken
                    raise ValueError(f"Code '{custom_code}' is already taken")
                logger.warning("Collision on code=%s, retrying", code)
                continue
            raise

    raise RuntimeError("Could not generate a unique code after retries")


def get_url(code: str) -> Optional[dict]:
    """Return the item for a code, or None if not found."""
    resp = table.get_item(Key={"code": code})
    return resp.get("Item")


def increment_clicks(code: str) -> None:
    """Best-effort click counter. Failures are logged but don't break the redirect."""
    try:
        table.update_item(
            Key={"code": code},
            UpdateExpression="ADD clicks :one",
            ExpressionAttributeValues={":one": 1},
        )
    except ClientError as e:
        logger.warning("Could not increment clicks for %s: %s", code, e)


def delete_url(code: str) -> bool:
    """Delete a short URL. Returns True if it existed, False otherwise."""
    try:
        table.delete_item(
            Key={"code": code},
            ConditionExpression="attribute_exists(code)",
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise