"""
One function per endpoint. Each returns an API Gateway response dict.
"""

import json
import logging
from urllib.parse import urlparse

from shortener import (
    create_short_url,
    get_url,
    increment_clicks,
    delete_url,
)
from config import MAX_URL_LENGTH

logger = logging.getLogger(__name__)


def _response(status_code: int, body: dict, extra_headers: dict = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    if extra_headers:
        headers.update(extra_headers)
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body),
    }


def _redirect(location: str) -> dict:
    return {
        "statusCode": 301,
        "headers": {
            "Location": location,
            "Access-Control-Allow-Origin": "*",
        },
        "body": "",
    }


def _base_url_from_event(event: dict) -> str:
    ctx = event.get("requestContext", {})
    domain = ctx.get("domainName", "")
    stage = ctx.get("stage", "$default")
    if stage == "$default" or not stage:
        return f"https://{domain}"
    return f"https://{domain}/{stage}"


def _validate_url(url: str) -> tuple[bool, str]:
    if not url or not isinstance(url, str):
        return False, "url is required"
    if len(url) > MAX_URL_LENGTH:
        return False, f"url exceeds {MAX_URL_LENGTH} characters"
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "url must start with http:// or https://"
    if not parsed.netloc:
        return False, "url is not valid"
    return True, ""


def handle_shorten(event: dict) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    url = (body.get("url") or "").strip()
    custom_code = body.get("code")

    is_valid, err = _validate_url(url)
    if not is_valid:
        return _response(400, {"error": err})

    if custom_code is not None:
        custom_code = custom_code.strip()
        if not custom_code or not custom_code.isalnum():
            return _response(400, {"error": "Custom code must be alphanumeric"})
        if len(custom_code) < 3 or len(custom_code) > 20:
            return _response(400, {"error": "Custom code must be 3-20 characters"})

    try:
        item = create_short_url(url, custom_code)
    except ValueError as e:
        return _response(409, {"error": str(e)})
    except Exception:
        logger.exception("Failed to create short URL")
        return _response(500, {"error": "Internal error"})

    base_url = _base_url_from_event(event)

    return _response(201, {
        "code": item["code"],
        "short_url": f"{base_url}/{item['code']}",
        "original_url": item["original_url"],
        "created_at": item["created_at"],
    })


def handle_redirect(code: str) -> dict:
    item = get_url(code)
    if not item:
        return _response(404, {"error": "Short URL not found"})
    increment_clicks(code)
    return _redirect(item["original_url"])


def handle_stats(code: str) -> dict:
    item = get_url(code)
    if not item:
        return _response(404, {"error": "Short URL not found"})
    return _response(200, {
        "code": item["code"],
        "original_url": item["original_url"],
        "clicks": int(item.get("clicks", 0)),
        "created_at": int(item.get("created_at", 0)),
        "expires_at": int(item["expires_at"]) if item.get("expires_at") else None,
    })


def handle_delete(code: str) -> dict:
    existed = delete_url(code)
    if not existed:
        return _response(404, {"error": "Short URL not found"})
    return _response(200, {"message": f"Deleted {code}"})
