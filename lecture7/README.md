# Lecture 7: Terraform - Chapters 1, 2, and 3

This folder contains the Terraform examples for Lecture 7. The material is based on *Terraform: Up and Running, 3rd Edition* by Yevgeniy Brikman.

## Chapter 1: Why Terraform

- Infrastructure as code: define infrastructure in code and deploy it with `terraform apply`
- Providers: Terraform can work with AWS, Azure, GCP, and other platforms
- `01_ch1_hello_terraform`: a very small EC2 example

## Chapter 2: Getting Started with Terraform

- Main Terraform blocks: `terraform`, `provider`, `resource`, `variable`, and `output`
- Basic commands: `terraform init`, `terraform plan`, `terraform apply`, and `terraform destroy`
- `02_ch2_one_server`: one EC2 instance
- `03_ch2_one_webserver`: one EC2 instance with a security group and a simple web server on port 8080
- `04_ch2_webserver_variables`: same web server example with variables
- `05_ch2_webserver_cluster`: Auto Scaling Group with an Application Load Balancer

## Chapter 3: Managing Terraform State

- Terraform keeps infrastructure information in `terraform.tfstate`
- Remote state can be stored in S3, with optional locking through DynamoDB
- Workspaces let you keep separate environments such as `dev`, `stage`, and `prod`
- `06_ch3_workspaces`: changes instance type based on `terraform.workspace`
- `07_ch3_remote_state`: creates resources for remote state storage

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.0
- AWS account and credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or `aws configure`)

## Running an Example

```bash
cd lecture7/01_ch1_hello_terraform
terraform init
terraform plan
terraform apply
terraform destroy
```

Each example folder has its own `README.md` with a short explanation and the commands needed to run it.

## Assignment: Web Server + n8n

The assignment for this lecture is to deploy a web server and `n8n`, making sure the dependencies start before `n8n`. The assignment can be done with Docker locally or with AWS.

- `assignment/docker/`: Docker solution where the web server container starts before the `n8n` container using `depends_on`
- `assignment/aws/`: AWS solution using one EC2 instance and a `user_data` script

See `LECTURE7_ASSIGNMENT_README.md` for the assignment steps and submission requirements.

## Reference

- Book: *Terraform: Up and Running*, 3rd Ed. - Chapters 1, 2, and 3
- Companion code: `terraform-up-and-running-code/code/terraform/`
