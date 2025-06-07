@echo off
cd /d %~dp0

echo 📦 Running targeted ECS task deployment...
terraform init

terraform apply -auto-approve -target=aws_ecs_task_definition.fastapi_task

echo ✅ Task definition update complete.
pause
