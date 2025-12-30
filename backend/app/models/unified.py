"""
Unified data models for fantasy football data.

These Pydantic models provide a platform-agnostic representation of fantasy
football data. Adapters transform platform-specific data into these unified
models, allowing the rest of the application to work with a consistent interface.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Enums for standardized values
# ============================================================================


class ScoringType(str, Enum):
    """Standard fantasy football scoring types."""

    STANDARD = "standard"
    PPR = "ppr"  # Points Per Reception
    HALF_PPR = "half_ppr"
    CUSTOM = "custom"


class DraftType(str, Enum):
    """Types of fantasy draft formats."""

    SNAKE = "snake"
    LINEAR = "linear"
    AUCTION = "auction"


class TransactionType(str, Enum):
    """Types of fantasy football transactions."""

    ADD = "add"
    DROP = "drop"
    TRADE = "trade"
    WAIVER = "waiver"


class PlayerPosition(str, Enum):
    """Standard fantasy football positions."""

    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    DST = "D/ST"  # Defense/Special Teams
    FLEX = "FLEX"
    BENCH = "BN"
    IR = "IR"  # Injured Reserve
    UNKNOWN = "UNKNOWN"


class RosterSlot(str, Enum):
    """Roster slot types for players."""

    STARTER = "starter"
    BENCH = "bench"
    IR = "ir"
    TAXI = "taxi"  # Taxi squad (dynasty leagues)


# ============================================================================
# Unified Models
# ============================================================================


class UnifiedLeague(BaseModel):
    """Unified representation of a fantasy football league.

    Contains league settings, scoring rules, and roster configuration
    normalized across different fantasy platforms.
    """

    id: str = Field(..., description="Platform-specific league identifier")
    platform: str = Field(..., description="Platform name (e.g., 'ESPN', 'Sleeper')")
    name: str = Field(..., description="League name")
    season: int = Field(..., description="Season year (e.g., 2024)")
    scoring_type: ScoringType = Field(..., description="Type of scoring system")

    # League structure
    num_teams: int = Field(..., description="Number of teams in the league")
    roster_positions: dict[str, int] = Field(
        default_factory=dict,
        description="Roster positions and their counts (e.g., {'QB': 1, 'RB': 2})",
    )

    # Playoff configuration
    playoff_teams: Optional[int] = Field(
        None, description="Number of teams that make playoffs"
    )
    playoff_start_week: Optional[int] = Field(
        None, description="Week when playoffs start"
    )

    # Platform-specific settings
    settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional platform-specific settings as key-value pairs",
    )

    model_config = {"use_enum_values": True}


class UnifiedTeam(BaseModel):
    """Unified representation of a fantasy team.

    Contains team information, owner details, and standings data
    normalized across different fantasy platforms.
    """

    id: str = Field(..., description="Platform-specific team identifier")
    league_id: str = Field(..., description="Platform-specific league identifier")
    name: str = Field(..., description="Team name")
    owner_name: Optional[str] = Field(None, description="Team owner's name")
    owner_id: Optional[str] = Field(None, description="Platform-specific owner ID")

    # Standings
    wins: int = Field(default=0, description="Number of wins")
    losses: int = Field(default=0, description="Number of losses")
    ties: int = Field(default=0, description="Number of ties")
    points_for: float = Field(default=0.0, description="Total points scored")
    points_against: float = Field(default=0.0, description="Total points allowed")

    # Additional team info
    waiver_position: Optional[int] = Field(None, description="Current waiver priority")
    draft_position: Optional[int] = Field(
        None, description="Draft position (snake order)"
    )
    division: Optional[str] = Field(None, description="Division name if applicable")

    # Platform-specific data
    extra_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional platform-specific team data"
    )

    model_config = {"use_enum_values": True}


class UnifiedPlayer(BaseModel):
    """Unified representation of a fantasy player.

    Contains player information and statistics normalized across
    different fantasy platforms.
    """

    id: str = Field(..., description="Platform-specific player identifier")
    name: str = Field(..., description="Player full name")
    position: PlayerPosition = Field(..., description="Player position")

    # NFL team info
    nfl_team: Optional[str] = Field(
        None, description="Current NFL team abbreviation (e.g., 'KC', 'SF')"
    )
    nfl_team_id: Optional[str] = Field(None, description="Platform-specific NFL team ID")

    # Roster info
    roster_slot: Optional[RosterSlot] = Field(
        None, description="Current roster slot (starter, bench, etc.)"
    )
    slot_position: Optional[str] = Field(
        None, description="Specific lineup position (e.g., 'RB1', 'FLEX')"
    )

    # Stats
    points: Optional[float] = Field(
        None, description="Fantasy points for current/specified week"
    )
    projected_points: Optional[float] = Field(
        None, description="Projected points for current/specified week"
    )

    # Status
    injury_status: Optional[str] = Field(
        None, description="Injury status (e.g., 'Out', 'Questionable', 'IR')"
    )
    is_active: bool = Field(
        default=True, description="Whether player is on an active roster"
    )

    # Platform-specific data
    extra_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional platform-specific player data"
    )

    model_config = {"use_enum_values": True}


class DraftPick(BaseModel):
    """Represents a single pick in a fantasy draft."""

    pick_number: int = Field(..., description="Overall pick number")
    round_number: int = Field(..., description="Round number")
    round_pick: int = Field(..., description="Pick number within the round")
    team_id: str = Field(..., description="ID of team that made the pick")
    player_id: str = Field(..., description="ID of player drafted")
    player_name: str = Field(..., description="Name of player drafted")
    bid_amount: Optional[float] = Field(
        None, description="Auction bid amount (if auction draft)"
    )


class UnifiedDraft(BaseModel):
    """Unified representation of a fantasy draft.

    Contains all draft picks with selection order normalized across
    different fantasy platforms.
    """

    league_id: str = Field(..., description="Platform-specific league identifier")
    season: int = Field(..., description="Season year")
    draft_type: DraftType = Field(..., description="Type of draft")
    draft_order: list[str] = Field(
        default_factory=list,
        description="Ordered list of team IDs representing draft order",
    )
    picks: list[DraftPick] = Field(
        default_factory=list, description="All draft picks in order"
    )

    # Draft metadata
    draft_date: Optional[datetime] = Field(None, description="When draft occurred")
    is_complete: bool = Field(default=False, description="Whether draft is complete")

    model_config = {"use_enum_values": True}


class UnifiedTransaction(BaseModel):
    """Unified representation of a fantasy transaction.

    Includes adds, drops, trades, and waiver claims normalized across
    different fantasy platforms.
    """

    id: str = Field(..., description="Platform-specific transaction identifier")
    league_id: str = Field(..., description="Platform-specific league identifier")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    timestamp: datetime = Field(..., description="When transaction occurred")

    # Teams involved
    team_ids: list[str] = Field(
        default_factory=list, description="IDs of teams involved in transaction"
    )

    # Players involved
    players_added: list[str] = Field(
        default_factory=list, description="Player IDs added in transaction"
    )
    players_dropped: list[str] = Field(
        default_factory=list, description="Player IDs dropped in transaction"
    )

    # Trade-specific
    is_trade: bool = Field(default=False, description="Whether this is a trade")
    trade_teams: Optional[dict[str, list[str]]] = Field(
        None,
        description="For trades: map of team_id to player_ids they received",
    )

    # Waiver-specific
    waiver_priority: Optional[int] = Field(
        None, description="Waiver priority used for claim"
    )
    faab_bid: Optional[float] = Field(
        None, description="FAAB (Free Agent Acquisition Budget) bid amount"
    )

    # Status
    status: str = Field(
        default="complete", description="Transaction status (complete, pending, vetoed)"
    )

    # Platform-specific data
    extra_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional platform-specific transaction data"
    )

    model_config = {"use_enum_values": True}


class UnifiedMatchup(BaseModel):
    """Unified representation of a weekly fantasy matchup.

    Contains head-to-head matchup data normalized across different
    fantasy platforms.
    """

    league_id: str = Field(..., description="Platform-specific league identifier")
    week: int = Field(..., description="Week number")

    # Teams
    home_team_id: str = Field(..., description="Home team identifier")
    away_team_id: Optional[str] = Field(
        None, description="Away team identifier (None for bye weeks)"
    )

    # Scores
    home_score: float = Field(default=0.0, description="Home team score")
    away_score: float = Field(default=0.0, description="Away team score")

    # Projected scores
    home_projected: Optional[float] = Field(
        None, description="Home team projected score"
    )
    away_projected: Optional[float] = Field(
        None, description="Away team projected score"
    )

    # Matchup metadata
    is_playoff: bool = Field(
        default=False, description="Whether this is a playoff matchup"
    )
    is_championship: bool = Field(
        default=False, description="Whether this is championship game"
    )
    is_consolation: bool = Field(
        default=False, description="Whether this is consolation bracket"
    )
    is_complete: bool = Field(
        default=False, description="Whether matchup is complete"
    )

    # Rosters (optional - can be populated with full roster data)
    home_roster: Optional[list[UnifiedPlayer]] = Field(
        None, description="Home team's roster for this week"
    )
    away_roster: Optional[list[UnifiedPlayer]] = Field(
        None, description="Away team's roster for this week"
    )

    # Platform-specific data
    extra_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional platform-specific matchup data"
    )

    model_config = {"use_enum_values": True}
