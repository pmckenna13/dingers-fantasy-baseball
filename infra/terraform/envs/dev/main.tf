terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Phase 0: state is local. Before the first real `apply`, switch this to
  # an S3 backend (+ DynamoDB lock table) so state isn't only on one laptop —
  # tracked as a Phase 1 infra task alongside standing up RDS/ElastiCache.
  # backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

locals {
  project     = "fantasy-baseball"
  environment = "dev"
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

  # Left at its placeholder default until the API image has been built and
  # pushed to ECR by CI (see .github/workflows/deploy.yml, added in Phase 1).
  # container_image = "${module.ecr_api.repository_url}:latest"
}
