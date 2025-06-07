@echo off
cd /d %~dp0

echo 🔄 Initializing Terraform...
terraform init

echo 🚀 Applying ECS Task Definition and Service Update...
terraform apply -auto-approve ^
  -target=aws_ecs_task_definition.fastapi_task ^
  -target=aws_ecs_service.backend_service

echo ✅ Redeployment complete!
pause
