from clearmetrics.ports.outbound.i_token_generator_port import ITokenGeneratorPort
from clearmetrics.ports.outbound.i_token_verifier_port import ITokenVerifierPort


class AuthService:
    """Handles token generation and verification via injected ports."""

    def __init__(
        self, generator: ITokenGeneratorPort, verifier: ITokenVerifierPort
    ) -> None:
        self._generator = generator
        self._verifier = verifier

    def generate_token(self, user_id: str, role: str) -> str:
        """Generate an authentication token for the given user and role."""
        return self._generator.generate_token(user_id=user_id, role=role)

    def verify_token(self, token: str) -> dict[str, str]:
        """Verify a token and return its decoded payload."""
        return self._verifier.verify_token(token=token)
