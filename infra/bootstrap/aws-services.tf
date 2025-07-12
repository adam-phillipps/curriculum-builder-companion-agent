# AWS Services Bootstrap
# Ensures required AWS services are enabled for the account

# Enable AWS Config (for compliance and monitoring)
resource "aws_config_configuration_recorder" "main" {
  name     = "curriculum-builder-config"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported = true
  }
}

# IAM Role for AWS Config
resource "aws_iam_role" "config" {
  name = "curriculum-builder-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "config" {
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}

# Enable CloudTrail (for audit logging)
resource "aws_cloudtrail" "main" {
  name           = "curriculum-builder-trail"
  s3_bucket_name = aws_s3_bucket.cloudtrail.bucket

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }
}

resource "aws_s3_bucket" "cloudtrail" {
  bucket        = "curriculum-builder-cloudtrail-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Service-linked roles (automatically created by AWS when needed)
# These are created automatically when services are first used:
# - AWSServiceRoleForECS
# - AWSServiceRoleForRDS
# - AWSServiceRoleForElastiCache
# - AWSServiceRoleForApplicationLoadBalancer