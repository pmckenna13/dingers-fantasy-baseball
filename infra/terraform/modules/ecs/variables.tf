variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "service_name" {
  type    = string
  default = "api"
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "alb_security_group_id" {
  type = string
}

variable "ecs_tasks_security_group_id" {
  type = string
}

variable "container_image" {
  type        = string
  description = <<-EOT
    Full image URI (e.g. <account>.dkr.ecr.<region>.amazonaws.com/repo:tag).
    Phase 0 default is a public placeholder that just serves a 200 on / so
    the pipeline (VPC -> ALB -> Fargate -> health check) can be proven end to
    end before the real API image exists in ECR.
  EOT
  default     = "public.ecr.aws/docker/library/nginx:stable"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "health_check_path" {
  type    = string
  default = "/api/v1/health"
}

variable "container_environment" {
  type    = map(string)
  default = {}
}

variable "task_cpu" {
  type    = number
  default = 256
}

variable "task_memory" {
  type    = number
  default = 512
}

variable "desired_count" {
  type    = number
  default = 1
}
