# Lecture 7: Web Server + n8n with Terraform

## Overview
Deployed a web server (nginx) and n8n (workflow automation) using Terraform with Docker provider. Ensured proper dependency order where n8n starts after the web server.
## Deployment
```bash
cd lecture7_assignment_webserver+n8n_Amine_Habbou
terraform init
terraform apply

Outputs
Web Server: http://localhost:8080
n8n: http://localhost:5678

Dependency Order
Web server container starts first
n8n container has depends_on = [docker_container.webserver] ensuring it starts after
Terraform manages the creation order automatically

Cleanup
'''bash
terraform destroy

Screenshots
webserver_screenshot.png: Web server page at localhost:8080
n8n_screenshot.png: n8n UI at localhost:5678