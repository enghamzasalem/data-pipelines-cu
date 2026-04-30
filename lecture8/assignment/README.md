LECTURE8_ASSIGNMENT_README.md << 'EOF'
# Lecture 8: Baseline Infrastructure (Docker)

## What This Deploys
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Storage (raw) | MinIO | Raw ingestion data |
| Storage (staged) | MinIO | Cleaned data |
| Database | PostgreSQL 15 | Pipeline metadata |

## Concepts Used
| Requirement | Where |
|-------------|-------|
| 2+ storage locations | 2 MinIO containers (raw, staged) |
| Database | PostgreSQL via modules/database |
| Reusable module | modules/storage + modules/database |
| for_each | modules/storage/main.tf |
| Variables | variables.tf at root + modules |
| Outputs | Bucket URLs, connection string |

## Run It
```bash
cd lecture8/assignment/docker
terraform init
terraform apply
```

## Outputs
- MinIO raw console: http://localhost:9001
- MinIO staged console: http://localhost:9003
- PostgreSQL: localhost:5432

## Destroy
```bash
terraform destroy
```
