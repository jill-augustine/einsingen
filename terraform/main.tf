# variables.tf
variable "AWS_REGION" {
  type    = string
  default = "eu-north-1"
}

# provider.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">=6.2.0"
    }
  }
}

provider "aws" {
  region = var.AWS_REGION
}
