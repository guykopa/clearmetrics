import jwt
from jwt.exceptions import InvalidTokenError

from clearmetrics.ports.outbound.i_token_verifier_port import ITokenVerifierPort


class JWTTokenVerifierAdapter(ITokenVerifierPort):
    """Verifies JWT tokens using PyJWT."""

    def __init__(self, secret: str, algorithm: str) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def verify_token(self, token: str) -> dict[str, str]:
        """Decode and verify a JWT, returning its payload."""
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return {"user_id": payload["user_id"], "role": payload["role"]}
        except (InvalidTokenError, KeyError) as exc:
            raise ValueError(f"Invalid token: {exc}") from exc
