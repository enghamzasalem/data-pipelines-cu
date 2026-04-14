# Lecture 7 Assignment: Web Server + n8n (AWS)

This folder contains the AWS version of the lecture 7 assignment.

Terraform creates one EC2 instance and uses `user_data` to:

1. install Docker
2. start the web server container
3. start the `n8n` container

This follows the professor's requirement that dependencies must run before `n8n`.

## Services

- Web server: `http://<public_ip>:8080`
- n8n: `http://<public_ip>:5678`

## Prerequisites

- Terraform
- AWS credentials configured locally
- A default VPC available in the selected region

## How to run

```bash
cd lecture7/assignment/aws
terraform init
terraform apply
```

After `terraform apply`, use:

```bash
terraform output webserver_url
terraform output n8n_url
```

Open both URLs in the browser and take the screenshots for submission.

## Clean up

```bash
terraform destroy
```
