# Get current AWS account ID and region for unique bucket names
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 Bucket for Frontend Assets
resource "aws_s3_bucket" "frontend" {
  bucket = "${var.environment}-curriculum-frontend-${substr(sha256("${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}-${var.environment}"), 0, 8)}"
  
  tags = merge(var.tags, {
    Name    = "${var.environment}-frontend-assets"
    Purpose = "frontend-hosting"
  })
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  index_document {
    suffix = "index.html"
  }
  
  error_document {
    key = "index.html"  # SPA routing
  }
}

# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${var.environment}-curriculum-frontend-oac"
  description                       = "OAC for curriculum frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
    origin_id                = "S3-${aws_s3_bucket.frontend.bucket}"
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.frontend.bucket}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  # SPA routing - redirect 404s to index.html
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = merge(var.tags, {
    Name = "${var.environment}-curriculum-frontend-cdn"
  })
}

# S3 Bucket Policy for CloudFront
resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })
}

# S3 Bucket for Learning Content Storage
resource "aws_s3_bucket" "content" {
  bucket = "${var.environment}-curriculum-content-${substr(sha256("${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}-${var.environment}-content"), 0, 8)}"
  
  tags = merge(var.tags, {
    Name    = "${var.environment}-learning-content"
    Purpose = "content-storage"
  })
}

resource "aws_s3_bucket_versioning" "content" {
  bucket = aws_s3_bucket.content.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "content" {
  bucket = aws_s3_bucket.content.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket for User Sandbox Artifacts
resource "aws_s3_bucket" "sandbox" {
  bucket = "${var.environment}-curriculum-sandbox-${substr(sha256("${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}-${var.environment}-sandbox"), 0, 8)}"
  
  tags = merge(var.tags, {
    Name    = "${var.environment}-sandbox-artifacts"
    Purpose = "sandbox-storage"
  })
}

resource "aws_s3_bucket_lifecycle_configuration" "sandbox" {
  bucket = aws_s3_bucket.sandbox.id
  
  rule {
    id     = "sandbox_cleanup"
    status = "Enabled"
    
    filter {
      prefix = ""
    }
    
    expiration {
      days = 30
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

