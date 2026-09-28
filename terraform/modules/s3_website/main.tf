resource "aws_s3_bucket" "this" {
  bucket        = var.bucket_name
  force_destroy = true
  tags          = var.tags
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  index_document {
    suffix = var.index_document
  }
}

data "aws_iam_policy_document" "public_read" {
  statement {
    sid    = "PublicReadGetObject"
    effect = "Allow"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.this.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "this" {
  bucket     = aws_s3_bucket.this.id
  policy     = data.aws_iam_policy_document.public_read.json
  depends_on = [aws_s3_bucket_public_access_block.this]
}

resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.this.id
  key          = var.index_document
  content_type = "text/html"

  content = templatefile("${var.source_dir}/${var.index_document}", {
    api_url = var.api_url
  })

  etag = md5(templatefile("${var.source_dir}/${var.index_document}", {
    api_url = var.api_url
  }))
}