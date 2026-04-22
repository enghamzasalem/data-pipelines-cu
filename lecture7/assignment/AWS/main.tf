terraform {
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

# Key Pair
resource "aws_key_pair" "deployer" {
  key_name   = "terraform-key"
  public_key = file(var.public_key_path)
}

# Security Group
resource "aws_security_group" "web_sg" {
  name = "terraform-web-sg"

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
}

# EC2 Instance
resource "aws_instance" "web" {
  ami           = "ami-096a4fdbcf530d8e0"
  instance_type = "t3.micro"

  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y

              amazon-linux-extras install docker -y
              service docker start
              usermod -a -G docker ec2-user

              # Web server FIRST
              docker run -d -p 8080:80 --name nginx nginx

              # n8n AFTER
              docker run -d -p 5678:5678 \
                -e N8N_BASIC_AUTH_ACTIVE=true \
                -e N8N_BASIC_AUTH_USER=admin \
                -e N8N_BASIC_AUTH_PASSWORD=admin \
                --name n8n n8nio/n8n
              EOF

  tags = {
    Name = "Terraform-n8n-server"
  }
}