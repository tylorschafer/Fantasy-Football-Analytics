"""
API endpoints for fantasy platform adapters.

Provides endpoints to query available adapters and their capabilities.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters import AdapterRegistry

router = APIRouter(prefix="/api/v1/adapters", tags=["adapters"])


class PlatformInfo(BaseModel):
    """Information about a registered platform adapter."""

    platform: str
    adapter_class: str
    is_available: bool = True


class PlatformsResponse(BaseModel):
    """Response containing list of available platforms."""

    count: int
    platforms: list[str]


@router.get("/platforms", response_model=PlatformsResponse)
async def list_platforms():
    """List all registered fantasy platform adapters.

    Returns a list of platform names that have registered adapters.
    These platforms can be used to connect to fantasy leagues.

    Returns:
        PlatformsResponse with count and list of platform names

    Example:
        GET /api/v1/adapters/platforms
        {
            "count": 3,
            "platforms": ["espn", "sleeper", "yahoo"]
        }
    """
    platforms = AdapterRegistry.list_platforms()
    return PlatformsResponse(count=len(platforms), platforms=platforms)


@router.get("/platforms/{platform}")
async def get_platform_info(platform: str):
    """Get information about a specific platform adapter.

    Args:
        platform: The platform name to query

    Returns:
        Platform information including availability and adapter class name

    Raises:
        HTTPException 404: If the platform is not registered

    Example:
        GET /api/v1/adapters/platforms/sleeper
        {
            "platform": "sleeper",
            "adapter_class": "SleeperAdapter",
            "is_available": true
        }
    """
    from fastapi import HTTPException

    if not AdapterRegistry.is_registered(platform):
        available = AdapterRegistry.list_platforms()
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Platform '{platform}' not registered",
                "available_platforms": available,
            },
        )

    adapter_class = AdapterRegistry.get_adapter_class(platform)

    return PlatformInfo(
        platform=platform,
        adapter_class=adapter_class.__name__,
        is_available=True,
    )
