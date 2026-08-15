# infra/terraform — AWS infrastructure as code

Phase 0 scope: enough to prove the deploy pipeline end-to-end (VPC → ALB →
ECS/Fargate → health check) before real app features exist. RDS and
ElastiCache are added in Phase 1 once there's a database schema to point
them at.

```
modules/
├── network/   VPC, public subnets, IGW, route table, ALB + task security groups
├── ecr/       Container image repository (with a lifecycle policy)
└── ecs/       ECS cluster, Fargate task/service, ALB + target group + listener
envs/
├── dev/       wires the modules together for the dev environment
└── prod/      same, sized for prod (desired_count = 2 for rolling deploys)
```

## Status: written, validated, **not applied**

`terraform fmt -check` and `terraform validate` pass for both `envs/dev` and
`envs/prod`. Nothing has been run against a real AWS account — `terraform
apply` needs your AWS credentials and is a real-money action (ALB + Fargate +
data transfer aren't free), so it's a deliberate, explicit next step with you
present, not something to run silently.

```bash
cd envs/dev
terraform init         # add an S3 backend first — see the commented `backend "s3" {}` block in main.tf
terraform plan
terraform apply
```

Until then, `container_image` defaults to a public nginx placeholder so the
service/ALB/health-check wiring can be proven before the real API image
exists in ECR — swap it for `${module.ecr_api.repository_url}:<tag>` once
Phase 1's deploy workflow is pushing real images.

## Not yet in place (intentional, tracked for later phases)

- **Remote state** (S3 + DynamoDB lock table) — state is local until the
  first real apply.
- **RDS / ElastiCache** — Phase 1, once the app has a schema and needs a
  cache/Pub/Sub bus.
- **Private subnets + NAT** — Phase 0 tasks get public IPs directly to avoid
  NAT gateway cost while there's nothing sensitive running; revisit once
  RDS/ElastiCache should sit off the public internet.
- **HTTPS on the ALB (ACM cert)** — added once there's a real domain.
