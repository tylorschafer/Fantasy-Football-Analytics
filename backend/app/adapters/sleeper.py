"""
Sleeper Fantasy Platform Adapter.

Implements the FantasyPlatformAdapter protocol for Sleeper's API.
API Documentation: https://docs.sleeper.com/
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.adapters.protocol import FantasyPlatformAdapter
from app.adapters.registry import AdapterRegistry
from app.models.unified import (
    DraftPick,
    DraftType,
    PlayerPosition,
    RosterSlot,
    ScoringType,
    TransactionType,
    UnifiedDraft,
    UnifiedLeague,
    UnifiedMatchup,
    UnifiedPlayer,
    UnifiedTeam,
    UnifiedTransaction,
)


@AdapterRegistry.register("sleeper")
class SleeperAdapter:
    """Adapter for Sleeper fantasy football platform.

    Sleeper provides a free, read-only API with no authentication required.
    Rate limit: 1000 requests per minute.

    API Base URL: https://api.sleeper.app/v1
    """

    platform_name = "sleeper"
    base_url = "https://api.sleeper.app/v1"

    def __init__(self):
        """Initialize the Sleeper adapter.

        No credentials required - Sleeper API is fully open.
        """
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"User-Agent": "FantasyAnalyzer/1.0"},
        )
        self._player_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None

    async def connect(self, credentials: dict) -> bool:
        """Validate connection to Sleeper API.

        Args:
            credentials: Not used for Sleeper (no auth required)

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Test connection by fetching NFL state
            response = await self.client.get("/state/nfl")
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def get_league(self, league_id: str, season: int) -> UnifiedLeague:
        """Fetch league information.

        Args:
            league_id: Sleeper league ID
            season: Season year (note: Sleeper league IDs are season-specific)

        Returns:
            UnifiedLeague with league settings and configuration
        """
        response = await self.client.get(f"/league/{league_id}")
        response.raise_for_status()
        data = response.json()

        # Map scoring type
        scoring_settings = data.get("scoring_settings", {})
        scoring_type = self._determine_scoring_type(scoring_settings)

        # Get roster positions
        roster_positions = self._count_roster_positions(
            data.get("roster_positions", [])
        )

        # Playoff configuration
        settings = data.get("settings", {})
        playoff_teams = settings.get("playoff_teams", 6)
        playoff_week_start = settings.get("playoff_week_start", 15)

        return UnifiedLeague(
            id=league_id,
            platform=self.platform_name,
            name=data.get("name", "Unknown League"),
            season=int(data.get("season", season)),
            scoring_type=scoring_type,
            num_teams=data.get("total_rosters", 0),
            roster_positions=roster_positions,
            playoff_teams=playoff_teams,
            playoff_start_week=playoff_week_start,
            settings={
                "draft_id": data.get("draft_id"),
                "status": data.get("status"),
                "sport": data.get("sport"),
                "season_type": data.get("season_type"),
                "settings": settings,
                "scoring_settings": scoring_settings,
            },
        )

    async def get_teams(self, league_id: str) -> List[UnifiedTeam]:
        """Fetch all teams in a league.

        Combines data from both /users and /rosters endpoints.

        Args:
            league_id: Sleeper league ID

        Returns:
            List of UnifiedTeam objects
        """
        # Fetch both users and rosters in parallel
        users_response, rosters_response = await asyncio.gather(
            self.client.get(f"/league/{league_id}/users"),
            self.client.get(f"/league/{league_id}/rosters"),
        )
        users_response.raise_for_status()
        rosters_response.raise_for_status()

        users_data = users_response.json()
        rosters_data = rosters_response.json()

        # Create a mapping of user_id to user data
        user_map = {user["user_id"]: user for user in users_data}

        teams = []
        for roster in rosters_data:
            owner_id = roster.get("owner_id")
            user = user_map.get(owner_id, {})

            # Get team name from user metadata or display name
            metadata = user.get("metadata", {})
            team_name = metadata.get("team_name") or user.get("display_name", "Unknown Team")

            settings = roster.get("settings", {})

            teams.append(
                UnifiedTeam(
                    id=str(roster["roster_id"]),
                    league_id=league_id,
                    name=team_name,
                    owner_name=user.get("display_name"),
                    owner_id=owner_id,
                    wins=settings.get("wins", 0),
                    losses=settings.get("losses", 0),
                    ties=settings.get("ties", 0),
                    points_for=float(settings.get("fpts", 0) + settings.get("fpts_decimal", 0) / 100),
                    points_against=float(
                        settings.get("fpts_against", 0)
                        + settings.get("fpts_against_decimal", 0) / 100
                    ),
                    waiver_position=settings.get("waiver_position"),
                    draft_position=roster.get("draft_slot"),
                    division=roster.get("division"),
                    extra_data={
                        "roster_id": roster["roster_id"],
                        "starters": roster.get("starters", []),
                        "reserve": roster.get("reserve", []),
                        "taxi": roster.get("taxi", []),
                        "waiver_budget_used": settings.get("waiver_budget_used", 0),
                        "total_moves": settings.get("total_moves", 0),
                    },
                )
            )

        return teams

    async def get_roster(
        self, league_id: str, team_id: str, week: Optional[int] = None
    ) -> List[UnifiedPlayer]:
        """Fetch roster for a specific team.

        Args:
            league_id: Sleeper league ID
            team_id: Roster ID (Sleeper uses roster_id as team identifier)
            week: Optional week number for matchup-specific roster

        Returns:
            List of UnifiedPlayer objects
        """
        # Get all rosters
        response = await self.client.get(f"/league/{league_id}/rosters")
        response.raise_for_status()
        rosters = response.json()

        # Find the specific roster
        roster = None
        for r in rosters:
            if str(r["roster_id"]) == str(team_id):
                roster = r
                break

        if not roster:
            return []

        # Get player data for name mapping
        await self._load_players()

        # Combine all player IDs from roster
        starters = roster.get("starters", [])
        reserve = roster.get("reserve", [])
        taxi = roster.get("taxi", [])
        all_players = roster.get("players", [])

        players = []
        for player_id in all_players:
            if not player_id:
                continue

            # Determine roster slot
            if player_id in starters:
                roster_slot = RosterSlot.STARTER
            elif player_id in reserve:
                roster_slot = RosterSlot.IR
            elif player_id in taxi:
                roster_slot = RosterSlot.TAXI
            else:
                roster_slot = RosterSlot.BENCH

            player = self._create_unified_player(player_id, roster_slot)
            players.append(player)

        return players

    async def get_draft(self, league_id: str) -> UnifiedDraft:
        """Fetch draft results for a league.

        Args:
            league_id: Sleeper league ID

        Returns:
            UnifiedDraft with all picks
        """
        # First get league to find draft_id
        league_response = await self.client.get(f"/league/{league_id}")
        league_response.raise_for_status()
        league_data = league_response.json()

        draft_id = league_data.get("draft_id")
        if not draft_id:
            # Return empty draft if no draft exists
            return UnifiedDraft(
                league_id=league_id,
                season=int(league_data.get("season", 2024)),
                draft_type=DraftType.SNAKE,
                is_complete=False,
            )

        # Fetch draft details and picks in parallel
        draft_response, picks_response = await asyncio.gather(
            self.client.get(f"/draft/{draft_id}"),
            self.client.get(f"/draft/{draft_id}/picks"),
        )
        draft_response.raise_for_status()
        picks_response.raise_for_status()

        draft_data = draft_response.json()
        picks_data = picks_response.json()

        # Determine draft type
        draft_type = DraftType.AUCTION if draft_data.get("type") == "auction" else DraftType.SNAKE

        # Get player names
        await self._load_players()

        # Convert picks to DraftPick objects
        picks = []
        for pick_data in picks_data:
            player_id = pick_data.get("player_id", "")
            player_info = self._player_cache.get(player_id, {}) if self._player_cache else {}

            picks.append(
                DraftPick(
                    pick_number=pick_data["pick_no"],
                    round_number=pick_data["round"],
                    round_pick=pick_data["draft_slot"],
                    team_id=str(pick_data["roster_id"]),
                    player_id=player_id,
                    player_name=self._get_player_name(player_id),
                    bid_amount=pick_data.get("metadata", {}).get("amount")
                    if draft_type == DraftType.AUCTION
                    else None,
                )
            )

        # Build draft order from slot_to_roster_id
        slot_to_roster = draft_data.get("slot_to_roster_id", {})
        draft_order = [str(slot_to_roster.get(str(i), "")) for i in range(1, len(slot_to_roster) + 1)]

        return UnifiedDraft(
            league_id=league_id,
            season=int(draft_data.get("season", 2024)),
            draft_type=draft_type,
            draft_order=draft_order,
            picks=picks,
            draft_date=datetime.fromtimestamp(draft_data["start_time"] / 1000)
            if draft_data.get("start_time")
            else None,
            is_complete=draft_data.get("status") == "complete",
        )

    async def get_transactions(
        self, league_id: str, start_date: Optional[datetime] = None
    ) -> List[UnifiedTransaction]:
        """Fetch transactions for a league.

        Args:
            league_id: Sleeper league ID
            start_date: Optional start date filter (Note: Sleeper uses rounds, not dates)

        Returns:
            List of UnifiedTransaction objects
        """
        # Sleeper requires fetching transactions by round (week)
        # We'll fetch all rounds and filter by date if needed

        # First get league to find current week/round
        league_response = await self.client.get(f"/league/{league_id}")
        league_response.raise_for_status()
        league_data = league_response.json()

        # Get current NFL state to determine rounds to fetch
        state_response = await self.client.get("/state/nfl")
        state_response.raise_for_status()
        state_data = state_response.json()

        current_week = state_data.get("week", 18)

        # Fetch transactions for all weeks
        all_transactions = []
        for round_num in range(1, current_week + 1):
            try:
                response = await self.client.get(
                    f"/league/{league_id}/transactions/{round_num}"
                )
                response.raise_for_status()
                transactions_data = response.json()
                all_transactions.extend(transactions_data)
            except Exception:
                # Some rounds may not have transactions
                continue

        # Convert to UnifiedTransaction
        transactions = []
        await self._load_players()

        for txn in all_transactions:
            timestamp = datetime.fromtimestamp(txn["created"] / 1000)

            # Filter by start_date if provided
            if start_date and timestamp < start_date:
                continue

            # Map transaction type
            txn_type = self._map_transaction_type(txn["type"])

            # Get adds and drops
            adds = txn.get("adds", {})
            drops = txn.get("drops", {})

            # Determine if it's a trade
            is_trade = txn["type"] == "trade"

            # Build trade teams mapping if it's a trade
            trade_teams = None
            if is_trade:
                trade_teams = {}
                for player_id, roster_id in adds.items():
                    roster_key = str(roster_id)
                    if roster_key not in trade_teams:
                        trade_teams[roster_key] = []
                    trade_teams[roster_key].append(player_id)

            # Get roster IDs involved
            roster_ids = set()
            if txn.get("roster_ids"):
                roster_ids.update(str(rid) for rid in txn["roster_ids"])
            else:
                # Infer from adds/drops
                for roster_id in adds.values():
                    roster_ids.add(str(roster_id))
                for roster_id in drops.values():
                    roster_ids.add(str(roster_id))

            transactions.append(
                UnifiedTransaction(
                    id=txn["transaction_id"],
                    league_id=league_id,
                    transaction_type=txn_type,
                    timestamp=timestamp,
                    team_ids=list(roster_ids),
                    players_added=list(adds.keys()),
                    players_dropped=list(drops.keys()),
                    is_trade=is_trade,
                    trade_teams=trade_teams,
                    waiver_priority=txn.get("settings", {}).get("waiver_position"),
                    faab_bid=txn.get("settings", {}).get("waiver_bid"),
                    status=txn.get("status", "complete"),
                )
            )

        return transactions

    async def get_matchups(self, league_id: str, week: int) -> List[UnifiedMatchup]:
        """Fetch matchups for a specific week.

        Args:
            league_id: Sleeper league ID
            week: Week number

        Returns:
            List of UnifiedMatchup objects
        """
        response = await self.client.get(f"/league/{league_id}/matchups/{week}")
        response.raise_for_status()
        matchups_data = response.json()

        # Group matchups by matchup_id
        matchup_groups: Dict[int, List[Any]] = {}
        for matchup in matchups_data:
            matchup_id = matchup.get("matchup_id")
            if matchup_id is None:
                continue  # Bye week
            if matchup_id not in matchup_groups:
                matchup_groups[matchup_id] = []
            matchup_groups[matchup_id].append(matchup)

        # Convert to UnifiedMatchup
        unified_matchups = []
        await self._load_players()

        for matchup_id, teams in matchup_groups.items():
            if len(teams) != 2:
                # Handle bye weeks or irregular matchups
                if len(teams) == 1:
                    team = teams[0]
                    unified_matchups.append(
                        UnifiedMatchup(
                            league_id=league_id,
                            week=week,
                            home_team_id=str(team["roster_id"]),
                            away_team_id=None,  # Bye week
                            home_score=float(team.get("points", 0)),
                            away_score=0.0,
                            is_complete=True,
                        )
                    )
                continue

            home_team = teams[0]
            away_team = teams[1]

            # Build rosters if starters are provided
            home_roster = None
            away_roster = None

            if home_team.get("starters"):
                home_roster = [
                    self._create_unified_player(pid, RosterSlot.STARTER)
                    for pid in home_team["starters"]
                    if pid
                ]

            if away_team.get("starters"):
                away_roster = [
                    self._create_unified_player(pid, RosterSlot.STARTER)
                    for pid in away_team["starters"]
                    if pid
                ]

            unified_matchups.append(
                UnifiedMatchup(
                    league_id=league_id,
                    week=week,
                    home_team_id=str(home_team["roster_id"]),
                    away_team_id=str(away_team["roster_id"]),
                    home_score=float(home_team.get("points", 0)),
                    away_score=float(away_team.get("points", 0)),
                    home_projected=home_team.get("custom_points"),
                    away_projected=away_team.get("custom_points"),
                    is_complete=True,  # Historical matchups are complete
                    home_roster=home_roster,
                    away_roster=away_roster,
                )
            )

        return unified_matchups

    # Helper methods

    async def _load_players(self) -> None:
        """Load player data from Sleeper API and cache it.

        Player data is ~5MB and should be cached with 24hr TTL.
        """
        # Check if cache is still valid (24 hours)
        if self._player_cache and self._cache_timestamp:
            age = datetime.now() - self._cache_timestamp
            if age.total_seconds() < 86400:  # 24 hours
                return

        # Fetch fresh player data
        response = await self.client.get("/players/nfl")
        response.raise_for_status()
        self._player_cache = response.json()
        self._cache_timestamp = datetime.now()

    def _get_player_name(self, player_id: str) -> str:
        """Get player name from ID using cached player data."""
        if not self._player_cache or not player_id:
            return "Unknown Player"

        player = self._player_cache.get(player_id, {})
        first_name = player.get("first_name", "")
        last_name = player.get("last_name", "")

        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif last_name:
            return last_name
        else:
            return "Unknown Player"

    def _create_unified_player(
        self, player_id: str, roster_slot: RosterSlot
    ) -> UnifiedPlayer:
        """Create a UnifiedPlayer from Sleeper player ID."""
        player_data = self._player_cache.get(player_id, {}) if self._player_cache else {}

        # Map position
        position_str = player_data.get("position", "UNKNOWN")
        try:
            position = PlayerPosition(position_str)
        except ValueError:
            position = PlayerPosition.UNKNOWN

        return UnifiedPlayer(
            id=player_id,
            name=self._get_player_name(player_id),
            position=position,
            nfl_team=player_data.get("team"),
            roster_slot=roster_slot,
            injury_status=player_data.get("injury_status"),
            is_active=player_data.get("active", False),
            extra_data={
                "age": player_data.get("age"),
                "college": player_data.get("college"),
                "years_exp": player_data.get("years_exp"),
                "status": player_data.get("status"),
            },
        )

    def _determine_scoring_type(self, scoring_settings: Dict[str, Any]) -> ScoringType:
        """Determine scoring type from Sleeper scoring settings."""
        # Check for PPR settings
        rec_score = scoring_settings.get("rec", 0)

        if rec_score == 1.0:
            return ScoringType.PPR
        elif rec_score == 0.5:
            return ScoringType.HALF_PPR
        elif rec_score == 0:
            return ScoringType.STANDARD
        else:
            return ScoringType.CUSTOM

    def _count_roster_positions(self, roster_positions: List[str]) -> Dict[str, int]:
        """Count roster positions from Sleeper's position list."""
        position_counts: Dict[str, int] = {}
        for pos in roster_positions:
            position_counts[pos] = position_counts.get(pos, 0) + 1
        return position_counts

    def _map_transaction_type(self, sleeper_type: str) -> TransactionType:
        """Map Sleeper transaction type to UnifiedTransaction type."""
        type_map = {
            "trade": TransactionType.TRADE,
            "waiver": TransactionType.WAIVER,
            "free_agent": TransactionType.ADD,
        }
        return type_map.get(sleeper_type, TransactionType.ADD)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
