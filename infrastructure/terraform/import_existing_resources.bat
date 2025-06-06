@echo off
echo 🔄 Importing existing AWS resources into Terraform state...

REM Import existing ECR repo
terraform import aws_ecr_repository.backend_repo lx-fta-backend

REM Import existing S3 bucket (frontend)
terraform import aws_s3_bucket.frontend_bucket lx-fta-frontend

REM Optional: Import DynamoDB table if already exists
REM terraform import aws_dynamodb_table.audit_logs lx_fta_audit_logs

echo ✅ Import completed. You can now run: terraform apply
pause
