# Terraform Assignment: First Webserver (Local)

## Overview

This project demonstrates how to deploy a simple web server locally using **Terraform** and **Docker**.
Terraform automatically provisions a Docker container running **nginx** and serves a custom HTML page.

The project shows a basic example of **Infrastructure as Code (IaC)** where infrastructure setup is automated using a Terraform configuration file.

---

## Technologies Used

* **Terraform** – Infrastructure as Code tool used to automate deployment
* **Docker** – Container platform used to run the nginx web server
* **nginx:alpine** – Lightweight web server image
* **HTML** – Simple webpage served by nginx

---

## Project Structure

```
terraform-assignment/
│
├── main.tf                # Terraform configuration
├── index.html             # HTML page served by nginx
├── README.md              # Project documentation
├── screenshot_page.png    # Screenshot of deployed webpage
└── screenshot_output.png  # Screenshot of terraform output
```

---

## How It Works

The Terraform configuration performs the following steps:

1. Pulls the **nginx:alpine Docker image**
2. Creates a local **index.html** webpage
3. Launches a Docker container running nginx
4. Mounts the project directory inside the container
5. Exposes the web server on **localhost:8081**

This allows the webpage to be accessed from a browser.

---

## Prerequisites

Before running the project, ensure the following are installed:

* Docker
* Terraform (version >= 1.0)

Verify installations:

```
docker --version
terraform version
```

Make sure the **Docker daemon is running**.

---

## Setup Instructions

### 1. Clone or Navigate to the Project

```
cd terraform-assignment
```

---

### 2. Initialize Terraform

```
terraform init
```

This command installs the required providers.

---

### 3. Deploy the Web Server

```
terraform apply
```

Confirm by typing:

```
yes
```

Terraform will automatically create the container and deploy the web page.

---

## Access the Web Page

Open the following URL in your browser:

```
http://localhost:8081
```

You should see the webpage deployed using Terraform.

---

## Terraform Outputs

After deployment Terraform prints:

```
local_url = http://localhost:8081
container_name = terraform-assignment-webserver
```

You can retrieve outputs later with:

```
terraform output
```

---

## Cleanup

To stop and remove the container:

```
terraform destroy
```

Confirm by typing:

```
yes
```

This removes all resources created by Terraform.

---

## Screenshots

The repository includes:

* **screenshot_page.png** – Browser showing the deployed webpage
* **screenshot_output.png** – Terraform output displaying the URL

---

## Author

Subhankar Biswas
Constructor University
Email: [subiswas@constructor.university](mailto:subiswas@constructor.university)

---

## Learning Outcome

This assignment demonstrates:

* Basic **Terraform workflow**
* Running containers with **Terraform Docker provider**
* Serving a static webpage using **nginx**
* Automating infrastructure setup with **Infrastructure as Code (IaC)**

---