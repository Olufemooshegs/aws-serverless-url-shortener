# ─────────────────────────────────────────────────────────────
# 1. DynamoDB (with TTL on expires_at)
# ─────────────────────────────────────────────────────────────
module "dynamodb" {
  source     = "../../modules/dynamodb"
  table_name = "${var.project_name}-${var.environment}"
}

# ─────────────────────────────────────────────────────────────
# 2. Lambda
#    - Env vars: TABLE_NAME, CODE_LENGTH, MAX_URL_LENGTH, DEFAULT_TTL_DAYS
#    - NO BASE_URL — derived from the request at runtime
# ─────────────────────────────────────────────────────────────
module "lambda" {
  source        = "../../modules/lambda"
  function_name = "${var.project_name}-${var.environment}"
  source_dir    = var.lambda_source_dir
  runtime       = "python3.12"
  handler       = "index.lambda_handler"

  environment_variables = {
    TABLE_NAME       = module.dynamodb.table_name
    CODE_LENGTH      = "7"
    MAX_URL_LENGTH   = "2048"
    DEFAULT_TTL_DAYS = "0"
  }

  dynamodb_table_arn = module.dynamodb.table_arn
}

# ─────────────────────────────────────────────────────────────
# 3. API Gateway (5 routes: POST /shorten, GET /stats/{code},
#    DELETE /{code}, GET /{code})
# ─────────────────────────────────────────────────────────────
module "api_gateway" {
  source               = "../../modules/api_gateway"
  api_name             = "${var.project_name}-${var.environment}-api"
  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.function_name
}

# ─────────────────────────────────────────────────────────────
# 4. S3 website
# ─────────────────────────────────────────────────────────────
data "aws_caller_identity" "current" {}

module "s3_website" {
  source      = "../../modules/s3_website"
  bucket_name = "${var.project_name}-${var.environment}-${data.aws_caller_identity.current.account_id}"
  source_dir  = var.frontend_source_dir
  api_url     = module.api_gateway.api_endpoint
}