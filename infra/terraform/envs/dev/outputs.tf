output "alb_dns_name" {
  value       = module.ecs_api.alb_dns_name
  description = "Public URL of the dev environment once applied and DNS has propagated."
}

output "ecr_repository_url" {
  value = module.ecr_api.repository_url
}
