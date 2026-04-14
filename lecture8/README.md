# Lecture 8: Terraform for Data Pipelines

This lecture focuses on baseline infrastructure for data pipelines using Terraform modules, loops, and reusable patterns.

## Topics

- Chapter 4: modules and reusable infrastructure
- Chapter 5: `count`, `for_each`, and Terraform expressions
- Chapter 6: secrets and Terraform state safety
- Chapter 7: working with multiple providers and environments

## Hands-on Lab

The `hands-on-lab/` folder contains a baseline AWS example with buckets and an optional database.

## Assignment: Baseline Infrastructure

The assignment for this lecture is to deploy storage plus a database or database-equivalent resource using modules and `for_each`.

- `assignment/aws/`: AWS solution with a reusable S3 bucket module, multiple buckets created with `for_each`, and a DynamoDB metadata table
- `assignment/docker/`: optional local route if Docker is available

See `LECTURE8_ASSIGNMENT_README.md` for the assignment details and submission requirements.

## Reference

- *Terraform: Up and Running*, 3rd Ed.
- Lecture 8 slides and hands-on lab
