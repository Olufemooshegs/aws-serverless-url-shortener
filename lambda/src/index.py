"""
Lambda entry point. Routes requests to handlers by method + path.

Routes:
    POST   /shorten         → create short URL
    GET    /stats/{code}    → stats for a code
    GET    /{code}          → redirect to original URL
    DELETE /{code}          → delete a short URL
"""

import json
import logging

from handlers import (
    handle_shorten,
    handle_redirect,
    handle_stats,
    handle_delete,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # API Gateway HTTP API v2 event format
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "")
    path = event.get("rawPath", "/")

    logger.info("Incoming: %s %s", method, path)

    # CORS preflight — API Gateway usually handles it, but just in case
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    # POST /shorten
    if method == "POST" and path == "/shorten":
        return handle_shorten(event)

    # GET /stats/{code}
    if method == "GET" and path.startswith("/stats/"):
        code = path[len("/stats/"):]
        if not code:
            return _not_found()
        return handle_stats(code)

    # DELETE /{code}
    if method == "DELETE" and len(path) > 1:
        return handle_delete(path.lstrip("/"))

    # GET /{code}  ← must be last — catch-all
    if method == "GET" and len(path) > 1:
        return handle_redirect(path.lstrip("/"))

    return _not_found()


def _not_found():
    return {
        "statusCode": 404,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"error": "Not found"}),
    }