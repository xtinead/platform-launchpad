terraform {
  backend "s3" {
    bucket         = "platform-launchpad-terraform-state"
    key            = "platform-launchpad/production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "platform-launchpad-terraform-locks"
    encrypt        = true
  }
}