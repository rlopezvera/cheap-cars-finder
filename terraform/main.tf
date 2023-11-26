terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_ecr_repository" "cheapo_ecr_repo" {
  name = var.cluster_name
}


resource "aws_ecs_cluster" "cheapo_cluster" {
  name = "cheapo-cluster" # Name your cluster here
}


# main.tf
resource "aws_ecs_task_definition" "cheapo_task" {
  family                   = "cheapo-first-task" # Name your task
  container_definitions    = <<DEFINITION
  [
    {
      "name": "cheapo-first-task",
      "image": "${aws_ecr_repository.cheapo_ecr_repo.repository_url}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000
        }
      ],
      "memory": 512,
      "cpu": 256
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"] # use Fargate as the launch type
  network_mode             = "awsvpc"    # add the AWS VPN network mode as this is required for Fargate
  memory                   = 512         # Specify the memory the container requires
  cpu                      = 256         # Specify the CPU the container requires
  execution_role_arn       = "${aws_iam_role.ecsTaskExecutionRole.arn}"
}

resource "aws_iam_role" "ecsTaskExecutionRole" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = "${aws_iam_role.ecsTaskExecutionRole.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "my_vpc"
  }
}

resource "aws_subnet" "my_subnet" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "my_subnet"
  }
}

resource "aws_security_group" "cheapo_security_group" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow traffic in from all sources
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_cloudwatch_event_rule" "daily_schedule" {
  name                = "run_daily_at_6_am_utc"
  description         = "Trigger ECS task daily at 6 AM UTC"
  schedule_expression = "cron(0 6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "run_ecs_task" {
  rule      = aws_cloudwatch_event_rule.daily_schedule.name
  target_id = "EcsTask"

  arn = aws_ecs_cluster.cheapo_cluster.arn

  role_arn = aws_iam_role.ecsTaskExecutionRole.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.cheapo_task.arn

    # If using Fargate, specify the launch type and network configuration
    launch_type         = "FARGATE"

    network_configuration {
      subnets = [aws_subnet.my_subnet.id]
      # Include security groups if necessary
      security_groups = [aws_security_group.cheapo_security_group.id]
      assign_public_ip = true # Set to false if not required
    }
  }
}

