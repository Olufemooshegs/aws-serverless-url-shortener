variable "bucket_name" {
  type = string
}

variable "index_document" {
  type    = string
  default = "index.html"
}

variable "source_dir" {
  type = string
}

variable "api_url" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
