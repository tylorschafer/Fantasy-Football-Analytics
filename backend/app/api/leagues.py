"""
API endpoints for league operations.

Provides endpoints to connect to fantasy leagues and fetch league data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.adapters import AdapterRegistry

router = APIRouter(prefix="/api/v1/leagues", tags=["leagues"])


class ConnectLeagueRequest(BaseModel):
    """Request to connect to a fantasy league."""

    platform: str
    league_id: str
    season: int


class ConnectLeagueResponse(BaseModel):
    """Response from connecting to a league."""

    success: bool
    message: str
    league: dict | None = None


@router.post("/connect", response_model=ConnectLeagueResponse)
async def connect_league(request: ConnectLeagueRequest):
    """Connect to a fantasy league and fetch its data.

    Args:
        request: League connection details (platform, league_id, season)

    Returns:
        ConnectLeagueResponse with league data if successful

    Raises:
        HTTPException 400: If platform is not supported
        HTTPException 404: If league not found
        HTTPException 500: If API request fails
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Attempting to connect to {request.platform} league {request.league_id}")

    # Validate platform
    if not AdapterRegistry.is_registered(request.platform):
        available = AdapterRegistry.list_platforms()
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Platform '{request.platform}' not supported",
                "available_platforms": available,
            },
        )

    try:
        # Get adapter instance
        adapter = AdapterRegistry.get(request.platform)
        logger.info(f"Got adapter for platform: {request.platform}")

        # Fetch league data
        logger.info(f"Fetching league data for {request.league_id}")
        league = await adapter.get_league(request.league_id, request.season)
        logger.info(f"League data fetched: {league.name}")

        # Fetch teams
        logger.info(f"Fetching teams for league {request.league_id}")
        teams = await adapter.get_teams(request.league_id)
        logger.info(f"Fetched {len(teams)} teams")

        # Convert to dict for response (using aliases for camelCase)
        league_dict = league.model_dump(by_alias=True)
        teams_dict = [team.model_dump(by_alias=True) for team in teams]

        response = ConnectLeagueResponse(
            success=True,
            message=f"Successfully connected to {league.name}",
            league={
                **league_dict,
                "teams": teams_dict,
            },
        )
        logger.info(f"Returning successful response for league {league.name}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        logger.error(f"Error connecting to league: {e}")
        logger.error(traceback.format_exc())

        error_message = str(e)

        # Check for common errors
        if "404" in error_message or "not found" in error_message.lower():
            raise HTTPException(
                status_code=404,
                detail=f"League '{request.league_id}' not found on {request.platform}",
            )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch league data: {error_message}",
        )


@router.get("/{platform}/{league_id}/{season}")
async def get_league(platform: str, league_id: str, season: int):
    """Get league data for a specific platform and league ID.

    Args:
        platform: Platform name (sleeper, espn, yahoo)
        league_id: Platform-specific league identifier
        season: Season year (e.g., 2024)

    Returns:
        League data with teams
    """
    # Use the connect endpoint logic
    request = ConnectLeagueRequest(
        platform=platform,
        league_id=league_id,
        season=season,
    )
    return await connect_league(request)
