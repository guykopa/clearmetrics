from abc import ABC, abstractmethod


class ITokenGeneratorPort(ABC):
    """Abstract port for generating authentication tokens."""

    @abstractmethod
    def generate_token(self, user_id: str, role: str) -> str:
        """Generate an authentication token for the given user."""
