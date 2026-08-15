terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # backend "s3" {}  # see envs/dev/main.tf note — required before first real apply.
}

provider "aws" {
  region = var.aws_region
}

locals {
  project     = "fantasy-baseball"
  environment = "prod"
}

module "network" {
  source = "../../modules/network"

  project     = local.project
  environment = local.environment
}

module "ecr_api" {
  source = "../../modules/ecr"

  project = local.project
  name    = "api"
}

module "ecs_api" {
  source = "../../modules/ecs"

  project     = local.project
  environment = local.environment
  aws_region  = var.aws_region

  vpc_id                      = module.network.vpc_id
  public_subnet_ids           = module.network.public_subnet_ids
  alb_security_group_id       = module.network.alb_security_group_id
  ecs_tasks_security_group_id = module.network.ecs_tasks_security_group_id

  # prod runs at least 2 tasks once the real image is live, for zero-downtime
  # rolling deploys — bumped from the module's dev-sized default of 1.
  desired_count = 2
}
