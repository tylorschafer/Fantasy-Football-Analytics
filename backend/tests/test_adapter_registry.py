"""
Tests for the AdapterRegistry.

Tests registration, instantiation, validation, and error handling.
"""

from datetime import datetime
from typing import List, Optional

import pytest

from app.adapters import AdapterRegistry, FantasyPlatformAdapter
from app.models.unified import (
    UnifiedDraft,
    UnifiedLeague,
    UnifiedMatchup,
    UnifiedPlayer,
    UnifiedTeam,
    UnifiedTransaction,
)


# Test fixtures and mock adapters
class MockAdapter:
    """Mock adapter implementing the FantasyPlatformAdapter protocol."""

    platform_name = "mock"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.connected = False

    async def connect(self, credentials: dict) -> bool:
        self.connected = True
        return True

    async def get_league(self, league_id: str, season: int) -> UnifiedLeague:
        return UnifiedLeague(
            id=league_id,
            platform=self.platform_name,
            name="Mock League",
            season=season,
            scoring_type="ppr",
            num_teams=12,
        )

    async def get_teams(self, league_id: str) -> List[UnifiedTeam]:
        return []

    async def get_roster(
        self, league_id: str, team_id: str, week: Optional[int] = None
    ) -> List[UnifiedPlayer]:
        return []

    async def get_draft(self, league_id: str) -> UnifiedDraft:
        return UnifiedDraft(league_id=league_id, season=2024, draft_type="snake")

    async def get_transactions(
        self, league_id: str, start_date: Optional[datetime] = None
    ) -> List[UnifiedTransaction]:
        return []

    async def get_matchups(self, league_id: str, week: int) -> List[UnifiedMatchup]:
        return []


class IncompleteAdapter:
    """Adapter missing required protocol methods."""

    platform_name = "incomplete"

    async def connect(self, credentials: dict) -> bool:
        return True

    # Missing other required methods


class InvalidAdapter:
    """Not a valid adapter (doesn't implement protocol)."""

    def some_method(self):
        pass


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the registry before and after each test."""
    AdapterRegistry.clear()
    yield
    AdapterRegistry.clear()


class TestAdapterRegistration:
    """Test adapter registration functionality."""

    def test_register_valid_adapter(self):
        """Test registering a valid adapter."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

        assert AdapterRegistry.is_registered("test")
        assert "test" in AdapterRegistry.list_platforms()

    def test_register_duplicate_platform_raises_error(self):
        """Test that registering the same platform twice raises ValueError."""

        @AdapterRegistry.register("duplicate")
        class FirstAdapter(MockAdapter):
            platform_name = "duplicate"

        with pytest.raises(ValueError, match="already registered"):

            @AdapterRegistry.register("duplicate")
            class SecondAdapter(MockAdapter):
                platform_name = "duplicate"

    def test_register_incomplete_adapter_raises_error(self):
        """Test that registering incomplete adapter raises TypeError."""
        with pytest.raises(TypeError, match="missing required protocol attributes"):

            @AdapterRegistry.register("incomplete")
            class TestIncomplete(IncompleteAdapter):
                pass

    def test_register_non_class_raises_error(self):
        """Test that registering non-class raises TypeError."""
        with pytest.raises(TypeError, match="must be a class"):

            @AdapterRegistry.register("invalid")
            def not_a_class():
                pass


class TestAdapterRetrieval:
    """Test adapter instantiation and retrieval."""

    def test_get_registered_adapter(self):
        """Test getting an instance of a registered adapter."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

        adapter = AdapterRegistry.get("test")
        assert isinstance(adapter, FantasyPlatformAdapter)
        assert adapter.platform_name == "test"

    def test_get_adapter_with_credentials(self):
        """Test getting adapter with credentials."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

        adapter = AdapterRegistry.get("test", api_key="secret123")
        assert adapter.api_key == "secret123"

    def test_get_unregistered_platform_raises_error(self):
        """Test that getting unregistered platform raises ValueError."""
        with pytest.raises(ValueError, match="Unknown platform"):
            AdapterRegistry.get("nonexistent")

    def test_get_with_invalid_credentials_raises_error(self):
        """Test that invalid credentials raise TypeError."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

            def __init__(self, required_param: str):
                self.required_param = required_param

        with pytest.raises(TypeError, match="Failed to instantiate"):
            AdapterRegistry.get("test")  # Missing required_param


class TestRegistryQueries:
    """Test registry query methods."""

    def test_list_platforms_empty(self):
        """Test list_platforms returns empty list when no adapters registered."""
        assert AdapterRegistry.list_platforms() == []

    def test_list_platforms_sorted(self):
        """Test list_platforms returns sorted list."""

        @AdapterRegistry.register("zebra")
        class ZebraAdapter(MockAdapter):
            platform_name = "zebra"

        @AdapterRegistry.register("apple")
        class AppleAdapter(MockAdapter):
            platform_name = "apple"

        @AdapterRegistry.register("banana")
        class BananaAdapter(MockAdapter):
            platform_name = "banana"

        platforms = AdapterRegistry.list_platforms()
        assert platforms == ["apple", "banana", "zebra"]

    def test_is_registered_true(self):
        """Test is_registered returns True for registered platform."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

        assert AdapterRegistry.is_registered("test") is True

    def test_is_registered_false(self):
        """Test is_registered returns False for unregistered platform."""
        assert AdapterRegistry.is_registered("nonexistent") is False

    def test_get_adapter_class(self):
        """Test getting adapter class without instantiation."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

        adapter_class = AdapterRegistry.get_adapter_class("test")
        assert adapter_class is TestAdapter
        assert adapter_class.platform_name == "test"

    def test_get_adapter_class_unregistered_raises_error(self):
        """Test get_adapter_class raises error for unregistered platform."""
        with pytest.raises(ValueError, match="Unknown platform"):
            AdapterRegistry.get_adapter_class("nonexistent")


class TestRegistryClear:
    """Test registry clearing functionality."""

    def test_clear_removes_all_adapters(self):
        """Test clear removes all registered adapters."""

        @AdapterRegistry.register("test1")
        class Test1Adapter(MockAdapter):
            platform_name = "test1"

        @AdapterRegistry.register("test2")
        class Test2Adapter(MockAdapter):
            platform_name = "test2"

        assert len(AdapterRegistry.list_platforms()) == 2

        AdapterRegistry.clear()

        assert len(AdapterRegistry.list_platforms()) == 0
        assert not AdapterRegistry.is_registered("test1")
        assert not AdapterRegistry.is_registered("test2")


@pytest.mark.asyncio
class TestAdapterProtocolCompliance:
    """Test that registered adapters work as expected via protocol."""

    async def test_adapter_methods_callable(self):
        """Test that adapter methods can be called through protocol."""

        @AdapterRegistry.register("test")
        class TestAdapter(MockAdapter):
            platform_name = "test"

        adapter = AdapterRegistry.get("test")

        # Test each protocol method
        assert await adapter.connect({}) is True

        league = await adapter.get_league("league123", 2024)
        assert league.id == "league123"
        assert league.season == 2024

        teams = await adapter.get_teams("league123")
        assert isinstance(teams, list)

        roster = await adapter.get_roster("league123", "team1", week=1)
        assert isinstance(roster, list)

        draft = await adapter.get_draft("league123")
        assert draft.league_id == "league123"

        transactions = await adapter.get_transactions("league123")
        assert isinstance(transactions, list)

        matchups = await adapter.get_matchups("league123", 1)
        assert isinstance(matchups, list)
