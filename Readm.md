# Project: LX-FTA Gateway – AWS Static Hosting with HTTPS

This project deploys a secure frontend for the **LX-FTA Gateway** using AWS services like S3, Route 53, ACM, CloudFront, ECR, and ECS. The infrastructure is managed via Terraform.

---

## 🔧 Project Structure
```
lx-fta-gateway/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── build_docker.py
      ── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── infrastructure/
│   ├── main.tf               # Terraform Infrastructure (S3, CloudFront, Route53, ACM, ECR, ECS)
│   ├── variables.tf          # Terraform variables
│   ├── outputs.tf            # Outputs like distribution domain and S3 URL
│   └── terraform.tfvars      # Actual values for variables
│
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions CI/CD Pipeline
│
├── scripts/
│   └── get_acm_cert.py       # Script to auto-fetch certificate ARN
│
├── README.md
└── .gitignore
```

---

## 🚀 Deployment Workflow (CI/CD)
This uses GitHub Actions to automate backend Docker builds and push to ECR, deploy to ECS, and deploy frontend to S3 + CloudFront.

**Workflow: .github/workflows/deploy.yml**
- On push to `main`:
  - Build Docker image for backend and push to ECR
  - Deploy backend to ECS
  - Build frontend and sync to S3 bucket
  - Invalidate CloudFront cache

---

## 🌐 Infrastructure Overview

### ✅ S3 Static Website Hosting
- Bucket: `lx-fta-frontend`
- Website configuration: `index.html` as root and fallback

### ✅ Route 53 DNS
- Hosted Zone: `lx-gateway.tech` (Created via Terraform)
- DNS Record: `portal.lx-gateway.tech` → CloudFront Distribution

### ✅ ACM SSL Certificate
- Issued for `portal.lx-gateway.tech`
- DNS validation managed via Terraform
- Fetched dynamically using `get_acm_cert.py`

### ✅ CloudFront Distribution
- HTTPS proxy for S3 using **Origin Access Control (OAC)**
- HTTP to HTTPS redirection
- Global content delivery

### ✅ Amazon ECR + ECS (Backend)
- Docker image pushed to `lx-fta-backend` ECR repository
- ECS Fargate service launches backend using the image

---

## 🔑 Pre-Requisites
- AWS CLI configured (`aws configure`)
- IAM user with access to S3, CloudFront, ACM, Route53, ECR, and ECS
- Terraform v1.5+
- Docker installed (for backend build)
- Python 3.x with `boto3`

---

## 📦 Terraform Commands
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

---

## 🌍 Output URL
```
https://portal.lx-gateway.tech