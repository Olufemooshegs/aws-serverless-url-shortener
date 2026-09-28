"""
Central config for the Lambda. Read env vars once at cold start.
"""

import os

TABLE_NAME = os.environ["TABLE_NAME"]
CODE_LENGTH = int(os.environ.get("CODE_LENGTH", "7"))
MAX_URL_LENGTH = int(os.environ.get("MAX_URL_LENGTH", "2048"))
DEFAULT_TTL_DAYS = int(os.environ.get("DEFAULT_TTL_DAYS", "0"))

# Note: BASE_URL is NOT read from env — it's derived from the incoming
# request (event.requestContext.domainName) to break a Terraform
# dependency cycle between Lambda and API Gateway.
