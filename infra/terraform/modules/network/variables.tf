variable "project" {
  type        = string
  description = "Project name, used as a prefix in resource names/tags."
}

variable "environment" {
  type        = string
  description = "Deployment environment, e.g. dev or prod."
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
  default     = "10.0.0.0/16"
}

variable "container_port" {
  type        = number
  description = "Port the ECS task listens on, used to scope the tasks security group."
  default     = 8000
}
