# FastAPI Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "${var.environment}-curriculum-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn           = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "db-migrate-init"
      image     = "${var.migrate_image}:${var.migrate_image_tag}"
      essential = false
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "REDIS_HOST"
          value = "localhost"
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "CHROMA_HOST"
          value = "localhost"
        },
        {
          name  = "CHROMA_PORT"
          value = "8000"
        }
      ]
      
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${var.secrets_arn}:database_url::"
        },
        {
          name      = "SECRET_KEY"
          valueFrom = "${var.secrets_arn}:secret_key::"
        },
        {
          name      = "POSTGRES_USER"
          valueFrom = "${var.secrets_arn}:postgres_user::"
        },
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = "${var.secrets_arn}:postgres_password::"
        },
        {
          name      = "POSTGRES_DB"
          valueFrom = "${var.secrets_arn}:postgres_db::"
        },
        {
          name      = "POSTGRES_HOST"
          valueFrom = "${var.secrets_arn}:postgres_host::"
        },
        {
          name      = "POSTGRES_PORT"
          valueFrom = "${var.secrets_arn}:postgres_port::"
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "${var.secrets_arn}:openai_api_key::"
        },
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = "${var.secrets_arn}:anthropic_api_key::"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.api_log_group
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "init-migrate"
        }
      }
    },
    {
      name      = "api"
      image     = "${var.api_image}:${var.api_image_tag}"
      dependsOn = [
        {
          containerName = "db-migrate-init"
          condition     = "SUCCESS"
        }
      ]
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "APP_ENV"
          value = var.environment == "production" ? "production" : "development"
        },
        {
          name  = "REDIS_HOST"
          value = var.redis_endpoint
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "CHROMA_HOST"
          value = "${var.environment}-curriculum-chromadb.${var.environment}-curriculum-cluster.local"
        },
        {
          name  = "CHROMA_PORT"
          value = "8000"
        }
      ]
      
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${var.secrets_arn}:database_url::"
        },
        {
          name      = "POSTGRES_USER"
          valueFrom = "${var.secrets_arn}:postgres_user::"
        },
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = "${var.secrets_arn}:postgres_password::"
        },
        {
          name      = "POSTGRES_DB"
          valueFrom = "${var.secrets_arn}:postgres_db::"
        },
        {
          name      = "POSTGRES_HOST"
          valueFrom = "${var.secrets_arn}:postgres_host::"
        },
        {
          name      = "POSTGRES_PORT"
          valueFrom = "${var.secrets_arn}:postgres_port::"
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "${var.secrets_arn}:openai_api_key::"
        },
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = "${var.secrets_arn}:anthropic_api_key::"
        },
        {
          name      = "SECRET_KEY"
          valueFrom = "${var.secrets_arn}:secret_key::"
        },
        {
          name      = "REDIS_AUTH_TOKEN"
          valueFrom = "${var.secrets_arn}:redis_auth_token::"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.api_log_group
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = var.tags
}

# ChromaDB Task Definition
resource "aws_ecs_task_definition" "chromadb" {
  family                   = "${var.environment}-curriculum-chromadb"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.chromadb_cpu
  memory                   = var.chromadb_memory
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn           = var.task_role_arn

  container_definitions = jsonencode([
    {
      name  = "chromadb"
      image = "${var.chromadb_image}:${var.chromadb_image_tag}"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "CHROMA_SERVER_HOST"
          value = "0.0.0.0"
        },
        {
          name  = "CHROMA_SERVER_HTTP_PORT"
          value = "8000"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.chromadb_log_group
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD", "chroma", "db", "list"]
        interval    = 30
        timeout     = 10
        retries     = 3
        startPeriod = 40
      }
    }
  ])

  tags = var.tags
}

# Database Migration Task Definition (run-once)
resource "aws_ecs_task_definition" "db_migrate" {
  family                   = "${var.environment}-curriculum-db-migrate"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn           = var.task_role_arn

  container_definitions = jsonencode([
    {
      name  = "db-migrate"
      image = "${var.migrate_image}:${var.migrate_image_tag}"
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "REDIS_HOST"
          value = "localhost"
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "CHROMA_HOST"
          value = "localhost"
        },
        {
          name  = "CHROMA_PORT"
          value = "8000"
        }
      ]
      
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${var.secrets_arn}:database_url::"
        },
        {
          name      = "SECRET_KEY"
          valueFrom = "${var.secrets_arn}:secret_key::"
        },
        {
          name      = "POSTGRES_USER"
          valueFrom = "${var.secrets_arn}:postgres_user::"
        },
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = "${var.secrets_arn}:postgres_password::"
        },
        {
          name      = "POSTGRES_DB"
          valueFrom = "${var.secrets_arn}:postgres_db::"
        },
        {
          name      = "POSTGRES_HOST"
          valueFrom = "${var.secrets_arn}:postgres_host::"
        },
        {
          name      = "POSTGRES_PORT"
          valueFrom = "${var.secrets_arn}:postgres_port::"
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "${var.secrets_arn}:openai_api_key::"
        },
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = "${var.secrets_arn}:anthropic_api_key::"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.api_log_group
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "db-migrate"
        }
      }
    }
  ])

  tags = var.tags
}

# Documentation Build Task Definition (run-once)
resource "aws_ecs_task_definition" "docs_build" {
  family                   = "${var.environment}-curriculum-docs-build"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn           = var.task_role_arn

  container_definitions = jsonencode([
    {
      name  = "docs-build"
      image = "${var.api_image}:${var.api_image_tag}"
      
      command = ["/app/scripts/entrypoint.sh", "docs"]
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "S3_DOCS_BUCKET"
          value = var.frontend_bucket_name
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.api_log_group
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "docs-build"
        }
      }
    }
  ])

  tags = var.tags
}

# API Service
resource "aws_ecs_service" "api" {
  name            = "${var.environment}-curriculum-api"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "api"
    container_port   = 8000
  }

  # depends_on = [var.alb_listener_arn]
  tags       = var.tags
}

# Service Discovery Namespace
resource "aws_service_discovery_private_dns_namespace" "main" {
  name = "${var.environment}-curriculum-cluster.local"
  vpc  = var.vpc_id
  
  tags = var.tags
}

# Service Discovery Service for ChromaDB
resource "aws_service_discovery_service" "chromadb" {
  name = "${var.environment}-curriculum-chromadb"
  
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    
    dns_records {
      ttl  = 10
      type = "A"
    }
    
    routing_policy = "MULTIVALUE"
  }
  
  health_check_grace_period_seconds = 30
  
  tags = var.tags
}

# ChromaDB Service
resource "aws_ecs_service" "chromadb" {
  name            = "${var.environment}-curriculum-chromadb"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.chromadb.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }
  
  service_registries {
    registry_arn = aws_service_discovery_service.chromadb.arn
  }

  tags = var.tags
}