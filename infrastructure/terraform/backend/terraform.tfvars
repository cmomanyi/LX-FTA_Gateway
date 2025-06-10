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
alb_arn = "arn:aws:elasticloadbalancing:us-east-1:263307268672:loadbalancer/app/ecs-alb/e9e12244e9f16dc1"

aws_region        = "us-east-1"
api_domain_name    = "api.lx-gateway.tech"
api_acm_cert_arn   = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
hosted_zone_id     = "Z0357093XHYR1IYCV5T3"
# alb_arn            = "arn:aws:elasticloadbalancing:us-east-1:263307268672:loadbalancer/app/ecs-alb/e9e12244e9f16dc1"
# target_group_arn  = "arn:aws:elasticloadbalancing:us-east-1:263307268672:targetgroup/ecs-tg/780f86453625e07d"