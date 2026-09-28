variable "function_name" {
  type = string
}

variable "source_dir" {
  type = string
}

variable "handler" {
  type    = string
  default = "index.lambda_handler"
}

variable "runtime" {
  type    = string
  default = "python3.12"
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}

variable "dynamodb_table_arn" {
  type        = string
  description = "ARN of the DynamoDB table the Lambda can access"
}

variable "tags" {
  type    = map(string)
  default = {}
}
