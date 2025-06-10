aws_region        = "us-east-1"
api_domain_name    = "api.lx-gateway.tech"
acm_cert_arn   = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
hosted_zone_id     = "Z0357093XHYR1IYCV5T3"
alb_arn            = "arn:aws:elasticloadbalancing:us-east-1:263307268672:loadbalancer/app/ecs-alb/e9e12244e9f16dc1"
target_group_arn  = "arn:aws:elasticloadbalancing:us-east-1:263307268672:targetgroup/ecs-tg/780f86453625e07d"
alb_zone_id         = "Z35SXDOTRQ7X7K"
alb_dns_name        = "ecs-alb-99933138.us-east-1.elb.amazonaws.com"
frontend_bucket_name = "lx-fta-frontend"
custom_domain_name   = "portal.lx-gateway.tech"
  # From Route53 for lx-gateway.tech
api_alb_dns_name = "ecs-alb-99933138.us-east-1.elb.amazonaws.com"
api_alb_zone_id  = "Z35SXDOTRQ7X7K"  # ALB hosted zone ID (static per region - see table below)



