# ─────────────────────────────────────────────────────────────
# The HTTP API
# ─────────────────────────────────────────────────────────────
resource "aws_apigatewayv2_api" "this" {
  name          = var.api_name
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type"]
    max_age       = 300
  }

  tags = var.tags
}

# ─────────────────────────────────────────────────────────────
# Single integration — all routes hit the same Lambda
# ─────────────────────────────────────────────────────────────
resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.lambda_invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# ─────────────────────────────────────────────────────────────
# Routes — this is the new part
#
# Route order in AWS matters: MORE SPECIFIC first, catch-all LAST.
# API Gateway uses the longest-prefix match, so /stats/{code} wins
# over /{code} when both match.
# ─────────────────────────────────────────────────────────────

# POST /shorten
resource "aws_apigatewayv2_route" "shorten" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "POST /shorten"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# GET /stats/{code}
resource "aws_apigatewayv2_route" "stats" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /stats/{code}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# DELETE /{code}
resource "aws_apigatewayv2_route" "delete" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "DELETE /{code}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# GET /{code} — catch-all, must be declared AFTER /stats/{code}
resource "aws_apigatewayv2_route" "redirect" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /{code}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# ─────────────────────────────────────────────────────────────
# Default stage — no /dev prefix in URL
# ─────────────────────────────────────────────────────────────
resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true
  tags        = var.tags
}

# ─────────────────────────────────────────────────────────────
# Permission for API Gateway to invoke Lambda
# ─────────────────────────────────────────────────────────────
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/*"
}