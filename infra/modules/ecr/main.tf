# ECR Repository for curriculum-api
resource "aws_ecr_repository" "curriculum_api" {
  name                 = "curriculum-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ECR Repository for curriculum-migrate
resource "aws_ecr_repository" "curriculum_migrate" {
  name                 = "curriculum-migrate"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ECR Repository for curriculum-docs
resource "aws_ecr_repository" "curriculum_docs" {
  name                 = "curriculum-docs"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ECR Lifecycle Policies
resource "aws_ecr_lifecycle_policy" "curriculum_api" {
  repository = aws_ecr_repository.curriculum_api.name
  policy = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "curriculum_migrate" {
  repository = aws_ecr_repository.curriculum_migrate.name
  policy = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "curriculum_docs" {
  repository = aws_ecr_repository.curriculum_docs.name
  policy = local.lifecycle_policy
}

locals {
  lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}