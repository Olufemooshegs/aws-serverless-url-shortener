terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Reusing the state bucket from the visitor-counter bootstrap.
    # Different `key` per project → separate state files in the same bucket.
    bucket         = "visitor-counter-tfstate-377c5a71"
    key            = "url-shortener/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "visitor-counter-tf-lock"
    encrypt        = true
  }
}