# Lecture 7 Assignment: Web Server + n8n (Docker)

This folder contains my Docker-based Terraform solution for the lecture 7 assignment.

It starts:

- an `nginx` web server on `http://localhost:8080`
- an `n8n` container on `http://localhost:5678`

The startup order is handled in Terraform:

- `local_file.index_html` is created first
- the web server depends on that file
- `n8n` depends on the web server container

Because of that, the web server starts before `n8n`.

## Files

- `main.tf`: Terraform configuration
- `index.html`: generated landing page for nginx

## Prerequisites

- Terraform
- Docker running locally

## How to run

```bash
cd lecture7/assignment/docker
terraform init
terraform apply
```

After `terraform apply`, you can open:

- `http://localhost:8080`
- `http://localhost:5678`

To print the URLs again later:

```bash
terraform output
```

## Clean up

```bash
terraform destroy
```

## Notes

- This solution uses the Docker option from `LECTURE7_ASSIGNMENT_README.md`
- The dependency order is implemented with `depends_on`
- Screenshots still need to be taken after running `terraform apply`
