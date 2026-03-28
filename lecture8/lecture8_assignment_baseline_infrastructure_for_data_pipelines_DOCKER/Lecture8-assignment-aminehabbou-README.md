# Lecture 8: Baseline Infrastructure (Docker) - Amine Habbou

## Overview
deployed an infrastructure that includes MinIO object storage with three buckets and PostgreSQL database for pipeline metadata.

## Infrastructure Components

### 1. Object Storage (MinIO)
- S3-compatible object storage running in Docker
- **Ports**: 9000 (API), 9001 (Console)
- **Buckets created** (using `for_each`):
  - `miniio-assignment8-amine-habbou-staging-raw-data`
  - `miniio-assignment8-amine-habbou-staging-processed-data`
  - `miniio-assignment8-amine-habbou-staging-analytics`

### 2. Database (PostgreSQL)
- PostgreSQL 15 running in Docker
- **Port**: 5432
- **Database**: `pipeline_metadata`
- Used for storing pipeline metadata and job tracking

### 3. Docker Network
- Isolated bridge network: `data-pipeline-network`
- Allows secure communication between containers

## Terraform Features Implemented

| Feature | Implementation |
|---------|---------------|
| **Modules** | Reusable `storage` and `database` modules in `/modules/` directory |
| **for_each** | Used to create 3 buckets dynamically from a list |
| **Variables** | Configurable project name, environment, credentials, bucket names |
| **Outputs** | Connection info, bucket names, endpoints (some marked sensitive) |


## Access Information

### MinIO Console (Web UI)
- **URL**: http://localhost:9001
- **Username**: `miniioass8`
- **Password**: `miniioass8`

### MinIO API
- **Endpoint**: http://localhost:9000
- **Compatible with**: AWS S3 SDK/CLI

### PostgreSQL Database
- **Host**: localhost
- **Port**: 5432
- **Database**: `pipeline_metadata`
- **Username**: `postgres`
- **Password**: `postgres123`

## Deployment Instructions

### Prerequisites
- Docker Desktop installed and running
- Terraform >= 1.0 installed
- Linux/WSL environment (for Unix socket) or Windows with named pipe

### Steps to Deploy
```bash
# Navigate to the docker directory
cd lecture8/assignment/docker

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the infrastructure
terraform apply
# Type 'yes' when prompted

# View outputs
terraform output

# Access MinIO Console
# Open browser: http://localhost:9001