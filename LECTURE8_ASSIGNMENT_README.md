# 🚀 Lecture 8: Terraform Assignment – Baseline Infrastructure for Data Pipelines

## 👨‍💻 Author

**Subhankar Biswas**

---

## 📌 Overview

This project demonstrates how to deploy a **baseline infrastructure for data pipelines** using **Terraform**, implemented in two environments:

* 🐳 **Docker (Local Development)**
* ☁️ **AWS (Cloud Deployment)**

The project showcases:

* Modular Terraform design
* Dynamic resource creation using `for_each`
* Infrastructure provisioning for storage and databases

---

# 🧭 Architecture Overview

## 🐳 Docker Architecture (Local)

* **MinIO** → S3-compatible object storage
* **PostgreSQL** → metadata database
* Runs locally using Docker containers

### Components

* 2 storage buckets:

  * `raw-data`
  * `staged-data`
* PostgreSQL database running on port `5432`
* MinIO console on `http://localhost:9001`

---

## ☁️ AWS Architecture (Cloud)

* 🪣 **Amazon S3**
* 🗄️ **Amazon RDS (PostgreSQL)**

### Components

* 3 S3 buckets:

  * `raw`
  * `staged`
  * `curated`
* RDS PostgreSQL instance
* Secure storage with:

  * Versioning
  * Encryption (AES256)

---

# 🎯 Objectives Achieved

* ✅ Multiple storage locations created
* ✅ Database deployed (PostgreSQL)
* ✅ Terraform modules implemented
* ✅ `for_each` used for dynamic resources
* ✅ Variables used for configuration
* ✅ Outputs generated for endpoints and resources

---

# 📁 Project Structure

```id="struct01"
lecture8/
├── assignment/
│   ├── docker/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   │       ├── storage/
│   │       │   ├── main.tf
│   │       │   ├── variables.tf
│   │       │   └── outputs.tf
│   │       └── database/
│   │           ├── main.tf
│   │           ├── variables.tf
│   │           └── outputs.tf
│   │
│   └── aws/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── modules/
│           ├── s3/
│           │   ├── main.tf
│           │   ├── variables.tf
│           │   └── outputs.tf
│           └── rds/
│               ├── main.tf
│               ├── variables.tf
│               └── outputs.tf
│
├── screenshot_docker.png
├── screenshot_s3.png
├── screenshot_rds.png
├── screenshot_output.png
└── LECTURE8_ASSIGNMENT_README.md
```

---

# 🐳 Docker Setup (Local)

## ⚙️ Prerequisites

* Docker installed and running
* Terraform installed

---

## 🚀 Run

```bash id="dock1"
cd assignment/docker
terraform init
terraform apply
```

---

## 🌐 Access

* MinIO Console → http://localhost:9001

  * Username: `minioadmin`
  * Password: `minioadmin`

* PostgreSQL → `localhost:5432`

---

## 📊 Outputs

```bash id="dock2"
terraform output
```

Example:

```id="dock3"
minio_console_url = "http://localhost:9001"
bucket_names = ["raw-data", "staged-data"]
postgres_connection = "postgresql://admin:password@localhost:5432/pipeline_db"
```

---

# ☁️ AWS Setup (Cloud)

## ⚙️ Prerequisites

* Terraform installed
* AWS CLI configured

---

## 🔧 Configure AWS

```bash id="aws1"
aws configure
```

Use:

* Region: `eu-central-1`
* Output: `json`

---

## 🔐 Set Variables

```bash id="aws2"
export TF_VAR_db_user='postgresuser'
export TF_VAR_db_password='StrongPass123!'
```

---

## 🚀 Deploy

```bash id="aws3"
cd assignment/aws
terraform init
terraform apply
```

---

## 📊 Outputs

```bash id="aws4"
terraform output
```

Example:

```id="aws5"
bucket_names = [...]
bucket_arns  = [...]
rds_endpoint = "xxxx.eu-central-1.rds.amazonaws.com:5432"
```

---

# 🧠 Key Terraform Concepts

## 🔁 for_each

Used to dynamically create multiple resources:

```id="code1"
for_each = var.buckets
```

---

## 🧱 Modules

* Docker:

  * `storage` (MinIO)
  * `database` (PostgreSQL)

* AWS:

  * `s3`
  * `rds`

---

## ⚙️ Variables & Outputs

* Variables for flexible configuration
* Outputs for:

  * URLs
  * Endpoints
  * Bucket names

---

# ⚠️ Challenges Faced

* Provider mismatch (Docker provider namespace)
* Deprecated attributes (`latest` → `image_id`)
* Docker daemon not running
* RDS username restrictions (`admin` not allowed)
* RDS password policy constraints
* Shell environment variable issue (`dquote` bug)

---

# 💡 Learnings

* Terraform modules improve maintainability
* `for_each` enables scalable infrastructure
* AWS services enforce strict validation rules
* Debugging Terraform requires reading error messages carefully

---

# 📸 Screenshots Included

* Docker containers running
* MinIO UI
* AWS S3 buckets
* AWS RDS instance
* Terraform outputs

---

# 💸 Cleanup (IMPORTANT)

## Docker

```bash id="clean1"
terraform destroy
```

## AWS (Avoid Charges)

```bash id="clean2"
terraform destroy
```

---

# ✅ Conclusion

This project successfully demonstrates:

* Local development using Docker
* Cloud deployment using AWS
* Modular and scalable infrastructure design using Terraform

---

# 🚀 Future Improvements

* VPC + private RDS setup
* IAM roles and security policies
* CI/CD integration
* Monitoring and logging
