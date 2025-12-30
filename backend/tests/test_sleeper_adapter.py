"""
Tests for the Sleeper adapter.

Tests API integration, data mapping, and error handling.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.sleeper import SleeperAdapter
from app.models.unified import (
    DraftType,
    PlayerPosition,
    RosterSlot,
    ScoringType,
    TransactionType,
)


# Mock response data
MOCK_LEAGUE_DATA = {
    "league_id": "123456789",
    "name": "Test League",
    "season": "2024",
    "total_rosters": 12,
    "status": "in_season",
    "sport": "nfl",
    "season_type": "regular",
    "scoring_settings": {"rec": 1.0, "pass_td": 4},
    "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "BN", "BN", "BN"],
    "settings": {
        "playoff_teams": 6,
        "playoff_week_start": 15,
    },
    "draft_id": "987654321",
}

MOCK_USERS_DATA = [
    {
        "user_id": "user1",
        "display_name": "Player One",
        "metadata": {"team_name": "Team One"},
    },
    {
        "user_id": "user2",
        "display_name": "Player Two",
        "metadata": {},
    },
]

MOCK_ROSTERS_DATA = [
    {
        "roster_id": 1,
        "owner_id": "user1",
        "players": ["player1", "player2"],
        "starters": ["player1"],
        "settings": {
            "wins": 8,
            "losses": 5,
            "ties": 0,
            "fpts": 1200,
            "fpts_decimal": 50,
            "fpts_against": 1100,
            "fpts_against_decimal": 0,
            "waiver_position": 3,
        },
        "draft_slot": 1,
    },
    {
        "roster_id": 2,
        "owner_id": "user2",
        "players": ["player3"],
        "starters": ["player3"],
        "settings": {
            "wins": 7,
            "losses": 6,
            "ties": 0,
            "fpts": 1150,
            "fpts_decimal": 0,
            "fpts_against": 1180,
            "fpts_against_decimal": 25,
        },
    },
]

MOCK_PLAYERS_DATA = {
    "player1": {
        "player_id": "player1",
        "first_name": "Patrick",
        "last_name": "Mahomes",
        "position": "QB",
        "team": "KC",
        "active": True,
        "injury_status": None,
    },
    "player2": {
        "player_id": "player2",
        "first_name": "Travis",
        "last_name": "Kelce",
        "position": "TE",
        "team": "KC",
        "active": True,
        "injury_status": None,
    },
    "player3": {
        "player_id": "player3",
        "first_name": "Christian",
        "last_name": "McCaffrey",
        "position": "RB",
        "team": "SF",
        "active": True,
        "injury_status": "Questionable",
    },
}

MOCK_DRAFT_DATA = {
    "draft_id": "987654321",
    "season": "2024",
    "type": "snake",
    "status": "complete",
    "start_time": 1704067200000,  # 2024-01-01 00:00:00
    "slot_to_roster_id": {"1": 1, "2": 2},
}

MOCK_DRAFT_PICKS_DATA = [
    {
        "player_id": "player1",
        "picked_by": "user1",
        "roster_id": 1,
        "round": 1,
        "draft_slot": 1,
        "pick_no": 1,
        "metadata": {},
    },
    {
        "player_id": "player2",
        "picked_by": "user1",
        "roster_id": 1,
        "round": 2,
        "draft_slot": 1,
        "pick_no": 13,
        "metadata": {},
    },
]

MOCK_MATCHUPS_DATA = [
    {
        "roster_id": 1,
        "matchup_id": 1,
        "points": 125.5,
        "starters": ["player1", "player2"],
        "custom_points": 120.0,
    },
    {
        "roster_id": 2,
        "matchup_id": 1,
        "points": 118.2,
        "starters": ["player3"],
        "custom_points": 115.0,
    },
]

MOCK_TRANSACTIONS_DATA = [
    {
        "transaction_id": "txn1",
        "type": "waiver",
        "status": "complete",
        "created": 1704153600000,  # 2024-01-02 00:00:00
        "roster_ids": [1],
        "adds": {"player1": 1},
        "drops": {"player2": 1},
        "settings": {"waiver_bid": 50, "waiver_position": 3},
    },
    {
        "transaction_id": "txn2",
        "type": "trade",
        "status": "complete",
        "created": 1704240000000,  # 2024-01-03 00:00:00
        "roster_ids": [1, 2],
        "adds": {"player3": 1, "player1": 2},
        "drops": {},
        "settings": {},
    },
]

MOCK_NFL_STATE = {
    "week": 14,
    "season": "2024",
    "season_type": "regular",
}


@pytest.fixture
def mock_adapter():
    """Create a SleeperAdapter with mocked HTTP client."""
    adapter = SleeperAdapter()
    adapter.client = AsyncMock()
    adapter._player_cache = MOCK_PLAYERS_DATA
    adapter._cache_timestamp = datetime.now()
    return adapter


@pytest.mark.asyncio
class TestSleeperAdapterConnection:
    """Test connection and initialization."""

    async def test_connect_success(self, mock_adapter):
        """Test successful connection to Sleeper API."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_NFL_STATE
        mock_adapter.client.get.return_value = mock_response

        result = await mock_adapter.connect({})

        assert result is True
        mock_adapter.client.get.assert_called_once_with("/state/nfl")

    async def test_connect_failure(self, mock_adapter):
        """Test connection failure handling."""
        mock_adapter.client.get.side_effect = Exception("Network error")

        result = await mock_adapter.connect({})

        assert result is False


@pytest.mark.asyncio
class TestSleeperAdapterLeague:
    """Test league data fetching."""

    async def test_get_league(self, mock_adapter):
        """Test fetching league data."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_LEAGUE_DATA
        mock_adapter.client.get.return_value = mock_response

        league = await mock_adapter.get_league("123456789", 2024)

        assert league.id == "123456789"
        assert league.name == "Test League"
        assert league.season == 2024
        assert league.platform == "sleeper"
        assert league.num_teams == 12
        assert league.scoring_type == ScoringType.PPR
        assert league.playoff_teams == 6
        assert league.playoff_start_week == 15
        assert "QB" in league.roster_positions
        assert league.roster_positions["QB"] == 1
        assert league.roster_positions["RB"] == 2

    async def test_get_league_half_ppr(self, mock_adapter):
        """Test league with half PPR scoring."""
        league_data = MOCK_LEAGUE_DATA.copy()
        league_data["scoring_settings"] = {"rec": 0.5}

        mock_response = MagicMock()
        mock_response.json.return_value = league_data
        mock_adapter.client.get.return_value = mock_response

        league = await mock_adapter.get_league("123456789", 2024)

        assert league.scoring_type == ScoringType.HALF_PPR

    async def test_get_league_standard(self, mock_adapter):
        """Test league with standard scoring."""
        league_data = MOCK_LEAGUE_DATA.copy()
        league_data["scoring_settings"] = {"rec": 0}

        mock_response = MagicMock()
        mock_response.json.return_value = league_data
        mock_adapter.client.get.return_value = mock_response

        league = await mock_adapter.get_league("123456789", 2024)

        assert league.scoring_type == ScoringType.STANDARD


@pytest.mark.asyncio
class TestSleeperAdapterTeams:
    """Test team data fetching."""

    async def test_get_teams(self, mock_adapter):
        """Test fetching teams."""
        users_response = MagicMock()
        users_response.json.return_value = MOCK_USERS_DATA

        rosters_response = MagicMock()
        rosters_response.json.return_value = MOCK_ROSTERS_DATA

        # Mock asyncio.gather - need to make it awaitable
        async def mock_gather_func(*args, **kwargs):
            return (users_response, rosters_response)

        with patch("app.adapters.sleeper.asyncio.gather", side_effect=mock_gather_func):
            teams = await mock_adapter.get_teams("123456789")

        assert len(teams) == 2

        # Check first team
        team1 = teams[0]
        assert team1.id == "1"
        assert team1.league_id == "123456789"
        assert team1.name == "Team One"
        assert team1.owner_name == "Player One"
        assert team1.wins == 8
        assert team1.losses == 5
        assert team1.ties == 0
        assert team1.points_for == 1200.5
        assert team1.points_against == 1100.0
        assert team1.waiver_position == 3
        assert team1.draft_position == 1

        # Check second team (uses display_name when no team_name)
        team2 = teams[1]
        assert team2.name == "Player Two"
        assert team2.wins == 7
        assert team2.losses == 6


@pytest.mark.asyncio
class TestSleeperAdapterRoster:
    """Test roster data fetching."""

    async def test_get_roster(self, mock_adapter):
        """Test fetching roster for a team."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ROSTERS_DATA
        mock_adapter.client.get.return_value = mock_response

        roster = await mock_adapter.get_roster("123456789", "1")

        assert len(roster) == 2

        # Check starter
        starter = next((p for p in roster if p.id == "player1"), None)
        assert starter is not None
        assert starter.roster_slot == RosterSlot.STARTER
        assert starter.name == "Patrick Mahomes"
        assert starter.position == PlayerPosition.QB
        assert starter.nfl_team == "KC"

        # Check bench
        bench = next((p for p in roster if p.id == "player2"), None)
        assert bench is not None
        assert bench.roster_slot == RosterSlot.BENCH

    async def test_get_roster_not_found(self, mock_adapter):
        """Test fetching roster for non-existent team."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ROSTERS_DATA
        mock_adapter.client.get.return_value = mock_response

        roster = await mock_adapter.get_roster("123456789", "999")

        assert len(roster) == 0


@pytest.mark.asyncio
class TestSleeperAdapterDraft:
    """Test draft data fetching."""

    async def test_get_draft(self, mock_adapter):
        """Test fetching draft data."""
        league_response = MagicMock()
        league_response.json.return_value = MOCK_LEAGUE_DATA

        draft_response = MagicMock()
        draft_response.json.return_value = MOCK_DRAFT_DATA

        picks_response = MagicMock()
        picks_response.json.return_value = MOCK_DRAFT_PICKS_DATA

        # First call returns league, second call mocks asyncio.gather
        mock_adapter.client.get.return_value = league_response

        # Mock asyncio.gather - need to make it awaitable
        async def mock_gather_func(*args, **kwargs):
            return (draft_response, picks_response)

        with patch("app.adapters.sleeper.asyncio.gather", side_effect=mock_gather_func):
            draft = await mock_adapter.get_draft("123456789")

        assert draft.league_id == "123456789"
        assert draft.season == 2024
        assert draft.draft_type == DraftType.SNAKE
        assert draft.is_complete is True
        assert len(draft.picks) == 2
        assert draft.draft_order == ["1", "2"]

        # Check first pick
        pick1 = draft.picks[0]
        assert pick1.pick_number == 1
        assert pick1.round_number == 1
        assert pick1.player_name == "Patrick Mahomes"
        assert pick1.team_id == "1"

    async def test_get_draft_no_draft_id(self, mock_adapter):
        """Test handling league with no draft."""
        league_data = MOCK_LEAGUE_DATA.copy()
        league_data["draft_id"] = None

        mock_response = MagicMock()
        mock_response.json.return_value = league_data
        mock_adapter.client.get.return_value = mock_response

        draft = await mock_adapter.get_draft("123456789")

        assert draft.is_complete is False
        assert len(draft.picks) == 0


@pytest.mark.asyncio
class TestSleeperAdapterTransactions:
    """Test transaction data fetching."""

    async def test_get_transactions(self, mock_adapter):
        """Test fetching transactions."""
        # Mock NFL state
        state_response = MagicMock()
        state_response.json.return_value = MOCK_NFL_STATE

        # Mock league response
        league_response = MagicMock()
        league_response.json.return_value = MOCK_LEAGUE_DATA

        # Mock transaction responses
        txn_response = MagicMock()
        txn_response.json.return_value = MOCK_TRANSACTIONS_DATA

        async def mock_get(url):
            if "/state/nfl" in url:
                return state_response
            elif "/transactions/" in url:
                return txn_response
            else:
                return league_response

        mock_adapter.client.get.side_effect = mock_get

        transactions = await mock_adapter.get_transactions("123456789")

        # Should have transactions from all weeks (mocked to return same data)
        assert len(transactions) > 0

        # Check waiver transaction
        waiver = next((t for t in transactions if t.transaction_type == TransactionType.WAIVER), None)
        assert waiver is not None
        assert waiver.waiver_priority == 3
        assert waiver.faab_bid == 50
        assert "player1" in waiver.players_added
        assert "player2" in waiver.players_dropped

        # Check trade transaction
        trade = next((t for t in transactions if t.is_trade), None)
        assert trade is not None
        assert trade.transaction_type == TransactionType.TRADE
        assert len(trade.team_ids) == 2


@pytest.mark.asyncio
class TestSleeperAdapterMatchups:
    """Test matchup data fetching."""

    async def test_get_matchups(self, mock_adapter):
        """Test fetching matchups for a week."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MATCHUPS_DATA
        mock_adapter.client.get.return_value = mock_response

        matchups = await mock_adapter.get_matchups("123456789", 1)

        assert len(matchups) == 1

        matchup = matchups[0]
        assert matchup.league_id == "123456789"
        assert matchup.week == 1
        assert matchup.home_team_id == "1"
        assert matchup.away_team_id == "2"
        assert matchup.home_score == 125.5
        assert matchup.away_score == 118.2
        assert matchup.home_projected == 120.0
        assert matchup.away_projected == 115.0
        assert matchup.is_complete is True

        # Check rosters
        assert matchup.home_roster is not None
        assert len(matchup.home_roster) == 2
        assert matchup.away_roster is not None
        assert len(matchup.away_roster) == 1

    async def test_get_matchups_with_bye(self, mock_adapter):
        """Test fetching matchups with bye week."""
        matchups_data = [
            {
                "roster_id": 1,
                "matchup_id": 1,
                "points": 125.5,
                "starters": ["player1"],
            },
            {
                "roster_id": 2,
                "matchup_id": None,  # Bye week
                "points": 0,
                "starters": [],
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = matchups_data
        mock_adapter.client.get.return_value = mock_response

        matchups = await mock_adapter.get_matchups("123456789", 1)

        # Should only have the non-bye matchup
        assert len(matchups) >= 1


class TestSleeperAdapterHelpers:
    """Test helper methods."""

    @pytest.mark.asyncio
    async def test_load_players_caching(self, mock_adapter):
        """Test that player data is cached properly."""
        # Clear cache
        mock_adapter._player_cache = None
        mock_adapter._cache_timestamp = None

        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_PLAYERS_DATA
        mock_adapter.client.get.return_value = mock_response

        # First load
        await mock_adapter._load_players()
        assert mock_adapter._player_cache == MOCK_PLAYERS_DATA
        assert mock_adapter._cache_timestamp is not None

        # Second load should use cache
        mock_adapter.client.get.reset_mock()
        await mock_adapter._load_players()
        mock_adapter.client.get.assert_not_called()

    def test_get_player_name(self, mock_adapter):
        """Test player name retrieval."""
        name = mock_adapter._get_player_name("player1")
        assert name == "Patrick Mahomes"

        name = mock_adapter._get_player_name("nonexistent")
        assert name == "Unknown Player"

    def test_determine_scoring_type(self, mock_adapter):
        """Test scoring type determination."""
        assert mock_adapter._determine_scoring_type({"rec": 1.0}) == ScoringType.PPR
        assert mock_adapter._determine_scoring_type({"rec": 0.5}) == ScoringType.HALF_PPR
        assert mock_adapter._determine_scoring_type({"rec": 0}) == ScoringType.STANDARD
        assert mock_adapter._determine_scoring_type({"rec": 0.75}) == ScoringType.CUSTOM

    def test_count_roster_positions(self, mock_adapter):
        """Test roster position counting."""
        positions = ["QB", "RB", "RB", "WR", "WR", "WR", "TE"]
        counts = mock_adapter._count_roster_positions(positions)

        assert counts["QB"] == 1
        assert counts["RB"] == 2
        assert counts["WR"] == 3
        assert counts["TE"] == 1

    def test_map_transaction_type(self, mock_adapter):
        """Test transaction type mapping."""
        assert mock_adapter._map_transaction_type("trade") == TransactionType.TRADE
        assert mock_adapter._map_transaction_type("waiver") == TransactionType.WAIVER
        assert mock_adapter._map_transaction_type("free_agent") == TransactionType.ADD
