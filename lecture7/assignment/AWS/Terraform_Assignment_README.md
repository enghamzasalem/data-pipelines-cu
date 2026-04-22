# 🚀 Terraform AWS EC2 Deployment with Docker (n8n + Nginx)

This project demonstrates provisioning cloud infrastructure on AWS using Terraform and deploying containerized applications (n8n + Nginx) on an EC2 instance.

---

## 📌 Project Overview

- Infrastructure as Code using **Terraform**
- AWS EC2 instance provisioning
- Secure access via **SSH key pair**
- Docker-based application deployment
- Exposing services via public IP

---

## 🏗️ Architecture

User → Browser → EC2 Instance (AWS)
                      ├── n8n (Port 5678)
                      └── Nginx (Port 8080)

---

## ⚙️ Tech Stack

- **Cloud:** AWS EC2
- **IaC:** Terraform
- **Containerization:** Docker
- **OS:** Amazon Linux 2023
- **Services:** n8n, Nginx

---

## 🔐 Setup Instructions

### 1. Install AWS CLI

```bash
brew install awscli
aws configure

Verify:
aws sts get-caller-identity

2. Generate SSH Key:
ssh-keygen -t rsa -b 4096 -f terraform-key
export TF_VAR_public_key_path="terraform-key.pub"

3. Initialize Terraform:
terraform init

4. Deploy Infrastructure:
terraform apply

🌐 Outputs:
After deployment:
n8n → http://18.157.180.149:5678/setup
Nginx → http://18.157.180.149:8080

⚠️ Issue Faced (Real Debugging Experience):
After deployment, services were not accessible in the browser.
Root Cause
user_data script failed
Amazon Linux 2023 uses dnf, not yum
Docker was not installed during provisioning

🛠️ Debugging Steps:
1. SSH into EC2:
ssh -i terraform-key ec2-user@<PUBLIC_IP>

2. Checked logs:
sudo cat /var/log/cloud-init-output.log

3. Identified Docker installation failure:

sudo dnf update -y
sudo dnf install -y docker

sudo systemctl start docker
sudo systemctl enable docker

sudo usermod -aG docker ec2-user

Reconnect SSH:
exit
ssh -i terraform-key ec2-user@<PUBLIC_IP>


🐳 Run Containers:
docker run -d -p 5678:5678 n8nio/n8n
docker run -d -p 8080:80 nginx

Verify:
docker ps

🔧 Final Fix (Terraform user_data):
#!/bin/bash
dnf update -y
dnf install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

docker run -d -p 5678:5678 n8nio/n8n
docker run -d -p 8080:80 nginx

🎯 Key Learnings:
Terraform provisioning vs application deployment are separate concerns
Importance of user_data reliability
Debugging via cloud-init logs
OS-specific package managers (yum vs dnf)
Docker permission handling (usermod + reconnect)

💡 Future Improvements:
Add HTTPS (Let's Encrypt)
Use Terraform modules
Add CI/CD pipeline (GitHub Actions)
Integrate with RDS / S3
Auto-scaling setup



















