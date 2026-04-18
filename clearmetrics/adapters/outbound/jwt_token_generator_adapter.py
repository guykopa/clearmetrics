import jwt

from clearmetrics.ports.outbound.i_token_generator_port import ITokenGeneratorPort


class JWTTokenGeneratorAdapter(ITokenGeneratorPort):
    """Generates JWT tokens using PyJWT."""

    def __init__(self, secret: str, algorithm: str) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def generate_token(self, user_id: str, role: str) -> str:
        """Generate a signed JWT containing user_id and role."""
        payload = {"user_id": user_id, "role": role}
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
