aws_region       = "us-east-1"
bucket_name      = "lx-fta-frontend"
domain_name       = "portal.lx-gateway.tech"
hosted_zone_name  = "lx-gateway.tech"


# Unique secret key used for JWT authentication
jwt_secret = "pkybZBce_EP-RppbW4y0DYxljiDvyPLs8tU9Vm1ezY8"  # replace with your generated key

# Your VPC ID (you can get this from AWS VPC dashboard)
vpc_id = "vpc-06c04252c22ad0822"

# Subnet IDs to place ECS tasks and ALB into (must be in same VPC)
subnet_ids = [
  "subnet-0eb6271aacb9f9714",
  "subnet-0cbda53eb585fec1d"

]
