# Lecture 8 Assignment: Baseline Infrastructure (AWS)

This folder contains the AWS solution for lecture 8.

The assignment requirements are covered like this:

- storage: three S3 buckets for `raw`, `staged`, and `curated`
- database equivalent: one DynamoDB table for pipeline metadata
- module: reusable `modules/s3-bucket`
- loop: `for_each` used to create the S3 buckets
- variables and outputs: root config uses variables and exports the bucket names, ARNs, and database details

## Structure

- `main.tf`: root resources and module calls
- `variables.tf`: root variables
- `outputs.tf`: root outputs
- `modules/s3-bucket/`: reusable S3 bucket module

## How to run

```bash
cd lecture8/assignment/aws
terraform init
terraform plan
terraform apply
```

## What gets created

- S3 buckets:
  - `data-pipeline-dev-raw-wezdar-cu`
  - `data-pipeline-dev-staged-wezdar-cu`
  - `data-pipeline-dev-curated-wezdar-cu`
- DynamoDB table:
  - `data-pipeline-dev-metadata`

## Outputs

- `bucket_names`
- `bucket_arns`
- `database_name`
- `database_arn`

## Clean up

```bash
terraform destroy
```
