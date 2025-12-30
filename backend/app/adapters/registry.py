"""
Adapter Registry for Fantasy Platform Adapters.

Provides centralized registration and instantiation of platform-specific
adapters using a singleton pattern with decorator-based registration.
"""

from typing import Any, Callable, Type

from app.adapters.protocol import FantasyPlatformAdapter


class AdapterRegistry:
    """Singleton registry for fantasy platform adapters.

    This registry allows dynamic registration of platform adapters using
    a decorator pattern and provides methods to instantiate and query
    registered adapters.

    Example:
        >>> @AdapterRegistry.register("sleeper")
        ... class SleeperAdapter:
        ...     platform_name = "sleeper"
        ...     async def connect(self, credentials): ...
        ...
        >>> adapter = AdapterRegistry.get("sleeper", api_key="xyz")
        >>> platforms = AdapterRegistry.list_platforms()
    """

    _adapters: dict[str, Type[FantasyPlatformAdapter]] = {}

    @classmethod
    def register(cls, platform: str) -> Callable:
        """Decorator to register an adapter class for a specific platform.

        Args:
            platform: The platform name (e.g., "sleeper", "espn", "yahoo").
                     Should be lowercase for consistency.

        Returns:
            Decorator function that registers the adapter class.

        Raises:
            TypeError: If the adapter class doesn't implement FantasyPlatformAdapter.
            ValueError: If the platform is already registered.

        Example:
            >>> @AdapterRegistry.register("sleeper")
            ... class SleeperAdapter:
            ...     platform_name = "sleeper"
            ...     # ... implement protocol methods
        """

        def decorator(adapter_class: Type[FantasyPlatformAdapter]) -> Type[FantasyPlatformAdapter]:
            # Validate that the adapter implements the protocol
            if not isinstance(adapter_class, type):
                raise TypeError(f"Adapter must be a class, got {type(adapter_class)}")

            # Check if platform is already registered
            if platform in cls._adapters:
                raise ValueError(
                    f"Platform '{platform}' is already registered with "
                    f"{cls._adapters[platform].__name__}"
                )

            # Runtime validation that the class implements the protocol
            # Note: Full protocol validation happens at runtime when methods are called
            required_attrs = ["platform_name", "connect", "get_league", "get_teams",
                            "get_roster", "get_draft", "get_transactions", "get_matchups"]

            missing_attrs = [attr for attr in required_attrs
                           if not hasattr(adapter_class, attr)]

            if missing_attrs:
                raise TypeError(
                    f"Adapter class {adapter_class.__name__} is missing required "
                    f"protocol attributes: {', '.join(missing_attrs)}"
                )

            # Register the adapter
            cls._adapters[platform] = adapter_class

            return adapter_class

        return decorator

    @classmethod
    def get(cls, platform: str, **credentials: Any) -> FantasyPlatformAdapter:
        """Get an adapter instance for the specified platform.

        Creates a new instance of the registered adapter for the given platform,
        passing any credentials as constructor arguments.

        Args:
            platform: The platform name (e.g., "sleeper", "espn", "yahoo")
            **credentials: Credentials and configuration to pass to the adapter
                          constructor (e.g., api_key, username, password)

        Returns:
            An instance of the platform adapter implementing FantasyPlatformAdapter

        Raises:
            ValueError: If the platform is not registered

        Example:
            >>> adapter = AdapterRegistry.get("sleeper", api_key="abc123")
            >>> league = await adapter.get_league("league_id", 2024)
        """
        if platform not in cls._adapters:
            available = ", ".join(cls._adapters.keys()) if cls._adapters else "none"
            raise ValueError(
                f"Unknown platform: '{platform}'. "
                f"Available platforms: {available}"
            )

        adapter_class = cls._adapters[platform]

        # Instantiate the adapter with credentials
        try:
            adapter_instance = adapter_class(**credentials)
        except TypeError as e:
            raise TypeError(
                f"Failed to instantiate {adapter_class.__name__} with provided "
                f"credentials. Error: {e}"
            ) from e

        # Final runtime check that instance implements the protocol
        if not isinstance(adapter_instance, FantasyPlatformAdapter):
            raise TypeError(
                f"{adapter_class.__name__} does not properly implement "
                f"FantasyPlatformAdapter protocol"
            )

        return adapter_instance

    @classmethod
    def list_platforms(cls) -> list[str]:
        """Return list of registered platform names.

        Returns:
            Sorted list of platform names that have registered adapters

        Example:
            >>> AdapterRegistry.list_platforms()
            ['espn', 'sleeper', 'yahoo']
        """
        return sorted(cls._adapters.keys())

    @classmethod
    def is_registered(cls, platform: str) -> bool:
        """Check if a platform adapter is registered.

        Args:
            platform: The platform name to check

        Returns:
            True if the platform has a registered adapter, False otherwise

        Example:
            >>> AdapterRegistry.is_registered("sleeper")
            True
            >>> AdapterRegistry.is_registered("unknown")
            False
        """
        return platform in cls._adapters

    @classmethod
    def clear(cls) -> None:
        """Clear all registered adapters.

        This method is primarily useful for testing to reset the registry
        state between tests.

        Warning:
            This will remove all registered adapters. Use with caution.
        """
        cls._adapters.clear()

    @classmethod
    def get_adapter_class(cls, platform: str) -> Type[FantasyPlatformAdapter]:
        """Get the adapter class (not instance) for a platform.

        Args:
            platform: The platform name

        Returns:
            The adapter class for the specified platform

        Raises:
            ValueError: If the platform is not registered

        Example:
            >>> adapter_class = AdapterRegistry.get_adapter_class("sleeper")
            >>> print(adapter_class.platform_name)
            'sleeper'
        """
        if platform not in cls._adapters:
            available = ", ".join(cls._adapters.keys()) if cls._adapters else "none"
            raise ValueError(
                f"Unknown platform: '{platform}'. "
                f"Available platforms: {available}"
            )

        return cls._adapters[platform]
