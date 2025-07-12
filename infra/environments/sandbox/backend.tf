terraform {
  backend "s3" {
    bucket         = "curriculum-builder-terraform-state-4503d1b4"
    key            = "environments/sandbox/terraform.tfstate"
    region         = "us-west-2"
    use_lockfile   = true
    encrypt        = true
  }
}