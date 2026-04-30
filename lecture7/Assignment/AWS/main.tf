terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}

# ── Data: latest Amazon Linux 2 AMI ──────────────────────────────────────────
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# ── Security Group ────────────────────────────────────────────────────────────
resource "aws_security_group" "lecture7_sg" {
  name        = "lecture7-sg"
  description = "Allow HTTP on 8080 (webserver) and 5678 (n8n)"

  ingress {
    description = "Web server"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "n8n"
    from_port   = 5678
    to_port     = 5678
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "lecture7-sg"
    Project = "lecture7"
  }
}

# ── EC2 Instance ──────────────────────────────────────────────────────────────
resource "aws_instance" "lecture7" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.lecture7_sg.id]

  # user_data runs on first boot in sequence:
  # 1. Install Docker
  # 2. Start webserver container  ← dependency
  # 3. Start n8n container        ← runs AFTER webserver
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # 1. Install Docker
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker

    # 2. Start webserver (nginx) — dependency
    docker run -d \
      --name webserver \
      --restart unless-stopped \
      -p 8080:80 \
      nginx:alpine

    # Wait for webserver to be healthy before starting n8n
    sleep 5

    # 3. Start n8n — runs AFTER webserver
    docker run -d \
      --name n8n \
      --restart unless-stopped \
      -p 5678:5678 \
      -e N8N_HOST=0.0.0.0 \
      -e N8N_PORT=5678 \
      -e N8N_PROTOCOL=http \
      -e WEBHOOK_URL=http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5678/ \
      n8nio/n8n:latest
  EOF

  tags = {
    Name    = "lecture7-webserver-n8n"
    Project = "lecture7"
  }
}
