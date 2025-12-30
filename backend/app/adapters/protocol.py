"""
Protocol definition for Fantasy Platform Adapters.

All platform-specific adapters (ESPN, Sleeper, Yahoo, etc.) must implement
this protocol to ensure consistent interface across different fantasy platforms.
"""

from datetime import datetime
from typing import List, Optional, Protocol, runtime_checkable


@runtime_checkable
class FantasyPlatformAdapter(Protocol):
    """Protocol defining the interface all platform adapters must implement.

    This protocol ensures that all fantasy platform adapters provide
    a consistent interface for fetching league data, regardless of the
    underlying platform (ESPN, Sleeper, Yahoo, etc.).

    Attributes:
        platform_name: The name of the fantasy platform (e.g., "ESPN", "Sleeper")
    """

    platform_name: str

    async def connect(self, credentials: dict) -> bool:
        """Authenticate and establish connection to the fantasy platform.

        Args:
            credentials: Platform-specific authentication credentials.
                        May include API keys, cookies, username/password, etc.

        Returns:
            True if connection successful, False otherwise.
        """
        ...

    async def get_league(self, league_id: str, season: int) -> "UnifiedLeague":
        """Fetch league information for a specific season.

        Args:
            league_id: Platform-specific league identifier
            season: The season year (e.g., 2024)

        Returns:
            UnifiedLeague object with league settings and configuration
        """
        ...

    async def get_teams(self, league_id: str) -> List["UnifiedTeam"]:
        """Fetch all teams in a league.

        Args:
            league_id: Platform-specific league identifier

        Returns:
            List of UnifiedTeam objects representing all teams in the league
        """
        ...

    async def get_roster(
        self, league_id: str, team_id: str, week: Optional[int] = None
    ) -> List["UnifiedPlayer"]:
        """Fetch roster for a specific team.

        Args:
            league_id: Platform-specific league identifier
            team_id: Platform-specific team identifier
            week: Optional week number. If None, returns current roster.

        Returns:
            List of UnifiedPlayer objects on the team's roster
        """
        ...

    async def get_draft(self, league_id: str) -> "UnifiedDraft":
        """Fetch draft results for a league.

        Args:
            league_id: Platform-specific league identifier

        Returns:
            UnifiedDraft object with all draft picks
        """
        ...

    async def get_transactions(
        self, league_id: str, start_date: Optional[datetime] = None
    ) -> List["UnifiedTransaction"]:
        """Fetch transactions (adds, drops, trades, waivers) for a league.

        Args:
            league_id: Platform-specific league identifier
            start_date: Optional start date to filter transactions.
                       If None, returns all transactions.

        Returns:
            List of UnifiedTransaction objects
        """
        ...

    async def get_matchups(self, league_id: str, week: int) -> List["UnifiedMatchup"]:
        """Fetch matchups for a specific week.

        Args:
            league_id: Platform-specific league identifier
            week: The week number

        Returns:
            List of UnifiedMatchup objects for the specified week
        """
        ...


# Import type hints for the protocol (will be available after unified models are created)
# This allows the protocol to reference the unified models in type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.unified import (
        UnifiedDraft,
        UnifiedLeague,
        UnifiedMatchup,
        UnifiedPlayer,
        UnifiedTeam,
        UnifiedTransaction,
    )
