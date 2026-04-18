from abc import ABC, abstractmethod


class ITokenVerifierPort(ABC):
    """Abstract port for verifying authentication tokens."""

    @abstractmethod
    def verify_token(self, token: str) -> dict[str, str]:
        """Verify a token and return its decoded payload."""
