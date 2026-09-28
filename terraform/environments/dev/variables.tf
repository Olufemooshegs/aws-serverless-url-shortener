variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "url-shortener"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "lambda_source_dir" {
  type    = string
  default = "../../../lambda/src"
}

variable "frontend_source_dir" {
  type    = string
  default = "../../../frontend"
}
