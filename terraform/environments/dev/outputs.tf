output "website_url" {
  description = "🌐 Open this in your browser"
  value       = "http://${module.s3_website.website_endpoint}"
}

output "api_endpoint" {
  description = "API base URL"
  value       = module.api_gateway.api_endpoint
}

output "dynamodb_table" {
  value = module.dynamodb.table_name
}

output "lambda_function" {
  value = module.lambda.function_name
}