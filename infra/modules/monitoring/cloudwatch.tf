/**
 * CloudWatch Logs configuration for application monitoring
 */

# Log group for API application logs
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/${var.environment}/curriculum-api/application"
  retention_in_days = var.log_retention_days
  
  tags = var.tags
}

# Log group for API access logs
resource "aws_cloudwatch_log_group" "api_access_logs" {
  name              = "/${var.environment}/curriculum-api/access"
  retention_in_days = var.log_retention_days
  
  tags = var.tags
}

# Log group for learning outcomes
resource "aws_cloudwatch_log_group" "learning_outcomes_logs" {
  name              = "/${var.environment}/curriculum-api/learning-outcomes"
  retention_in_days = var.log_retention_days
  
  tags = var.tags
}



# Log metric filter for API errors
resource "aws_cloudwatch_log_metric_filter" "api_errors" {
  name           = "${var.environment}-api-errors"
  pattern        = "{ $.level = \"ERROR\" }"
  log_group_name = aws_cloudwatch_log_group.api_logs.name

  metric_transformation {
    name      = "${var.environment}ApiErrors"
    namespace = "CurriculumBuilder"
    value     = "1"
  }
}

# Log metric filter for learning outcome creation failures
resource "aws_cloudwatch_log_metric_filter" "learning_outcome_creation_failures" {
  name           = "${var.environment}-learning-outcome-creation-failures"
  pattern        = "{ $.message = \"*Failed to create learning outcome*\" }"
  log_group_name = aws_cloudwatch_log_group.learning_outcomes_logs.name

  metric_transformation {
    name      = "${var.environment}LearningOutcomeCreationFailures"
    namespace = "CurriculumBuilder"
    value     = "1"
  }
}

# CloudWatch alarm for high error rate
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.environment}-high-api-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "${var.environment}ApiErrors"
  namespace           = "CurriculumBuilder"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This alarm monitors for high API error rates"
  treat_missing_data  = "notBreaching"
  
  tags = var.tags
}

# CloudWatch dashboard for application monitoring
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.environment}-curriculum-builder"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["CurriculumBuilder", "${var.environment}ApiErrors"]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "API Errors"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.api_logs.name}' | fields @timestamp, @message, level, request_id, path, method, status_code | filter level = 'ERROR' | sort @timestamp desc | limit 20"
          region  = var.aws_region
          title   = "Recent API Errors"
          view    = "table"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.learning_outcomes_logs.name}' | fields @timestamp, @message, level, request_id, path, method | sort @timestamp desc | limit 20"
          region  = var.aws_region
          title   = "Learning Outcomes Activity"
          view    = "table"
        }
      }
    ]
  })
}