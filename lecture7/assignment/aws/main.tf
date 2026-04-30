terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_security_group" "lecture7" {
  name        = var.security_group_name
  description = "Security group for lecture 7 web server and n8n"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5678
    to_port     = 5678
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
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
    Name = var.security_group_name
  }
}

resource "aws_instance" "lecture7" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.lecture7.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    amazon-linux-extras install docker -y
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ec2-user

    mkdir -p /opt/lecture7
    cat > /opt/lecture7/index.html <<'HTML'
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Lecture 7 AWS Assignment</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: #f8fafc;
          color: #0f172a;
          margin: 0;
          min-height: 100vh;
          display: grid;
          place-items: center;
        }
        main {
          max-width: 700px;
          margin: 24px;
          padding: 32px;
          background: white;
          border-radius: 16px;
          box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
        }
      </style>
    </head>
    <body>
      <main>
        <h1>Lecture 7: Web Server + n8n on AWS</h1>
        <p>This page is served from an EC2 instance provisioned with Terraform.</p>
        <p>The web server container is started before the n8n container.</p>
      </main>
    </body>
    </html>
    HTML

    docker run -d \
      --name lecture7-webserver \
      -p 8080:80 \
      -v /opt/lecture7/index.html:/usr/share/nginx/html/index.html:ro \
      nginx:alpine

    docker run -d \
      --name lecture7-n8n \
      -p 5678:5678 \
      -e N8N_HOST=0.0.0.0 \
      -e N8N_PORT=5678 \
      -e N8N_PROTOCOL=http \
      -e N8N_SECURE_COOKIE=false \
      n8nio/n8n:latest
  EOF

  user_data_replace_on_change = true

  tags = {
    Name = "lecture7-webserver-n8n"
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "security_group_name" {
  type    = string
  default = "lecture7-webserver-n8n-sg"
}

output "public_ip" {
  value       = aws_instance.lecture7.public_ip
  description = "Public IP address of the lecture 7 EC2 instance"
}

output "webserver_url" {
  value       = "http://${aws_instance.lecture7.public_ip}:8080"
  description = "URL of the lecture 7 web server"
}

output "n8n_url" {
  value       = "http://${aws_instance.lecture7.public_ip}:5678"
  description = "URL of the lecture 7 n8n instance"
}
