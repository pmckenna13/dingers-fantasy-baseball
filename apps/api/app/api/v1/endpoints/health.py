from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe for local docker-compose and the ECS/ALB target group."""
    return {"status": "ok"}
