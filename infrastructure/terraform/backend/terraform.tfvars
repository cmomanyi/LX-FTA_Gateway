aws_region       = "us-east-1"



# Unique secret key used for JWT authentication
jwt_secret = "pkybZBce_EP-RppbW4y0DYxljiDvyPLs8tU9Vm1ezY8"  # replace with your generated key

# Your VPC ID (you can get this from AWS VPC dashboard)
vpc_id = "vpc-06c04252c22ad0822"

# Subnet IDs to place ECS tasks and ALB into (must be in same VPC)
subnet_ids = [
  "subnet-0a089563aaf84e900",
  "subnet-0a43a8f0719857ca3"
  ]
