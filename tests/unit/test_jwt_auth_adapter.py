import pytest
from clearmetrics.adapters.outbound.jwt_token_generator_adapter import JWTTokenGeneratorAdapter
from clearmetrics.adapters.outbound.jwt_token_verifier_adapter import JWTTokenVerifierAdapter
from clearmetrics.ports.outbound.i_token_generator_port import ITokenGeneratorPort
from clearmetrics.ports.outbound.i_token_verifier_port import ITokenVerifierPort

SECRET = "test-secret-key-minimum-32-bytes!!"
ALGORITHM = "HS256"


class TestJWTTokenGeneratorAdapter:
    def test_implements_port(self) -> None:
        adapter = JWTTokenGeneratorAdapter(secret=SECRET, algorithm=ALGORITHM)
        assert isinstance(adapter, ITokenGeneratorPort)

    def test_generate_returns_non_empty_string(self) -> None:
        adapter = JWTTokenGeneratorAdapter(secret=SECRET, algorithm=ALGORITHM)
        token = adapter.generate_token(user_id="usr-001", role="admin")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_returns_jwt_format(self) -> None:
        adapter = JWTTokenGeneratorAdapter(secret=SECRET, algorithm=ALGORITHM)
        token = adapter.generate_token(user_id="usr-001", role="admin")
        assert token.count(".") == 2

    def test_different_users_get_different_tokens(self) -> None:
        adapter = JWTTokenGeneratorAdapter(secret=SECRET, algorithm=ALGORITHM)
        token_a = adapter.generate_token(user_id="usr-001", role="admin")
        token_b = adapter.generate_token(user_id="usr-002", role="viewer")
        assert token_a != token_b


class TestJWTTokenVerifierAdapter:
    def test_implements_port(self) -> None:
        adapter = JWTTokenVerifierAdapter(secret=SECRET, algorithm=ALGORITHM)
        assert isinstance(adapter, ITokenVerifierPort)

    def test_verify_returns_correct_payload(self) -> None:
        generator = JWTTokenGeneratorAdapter(secret=SECRET, algorithm=ALGORITHM)
        verifier = JWTTokenVerifierAdapter(secret=SECRET, algorithm=ALGORITHM)
        token = generator.generate_token(user_id="usr-001", role="analyst")
        payload = verifier.verify_token(token)
        assert payload["user_id"] == "usr-001"
        assert payload["role"] == "analyst"

    def test_verify_raises_on_invalid_token(self) -> None:
        verifier = JWTTokenVerifierAdapter(secret=SECRET, algorithm=ALGORITHM)
        with pytest.raises(ValueError):
            verifier.verify_token("not.a.valid.token")

    def test_verify_raises_on_wrong_secret(self) -> None:
        generator = JWTTokenGeneratorAdapter(secret=SECRET, algorithm=ALGORITHM)
        verifier = JWTTokenVerifierAdapter(secret="wrong-secret", algorithm=ALGORITHM)
        token = generator.generate_token(user_id="usr-001", role="admin")
        with pytest.raises(ValueError):
            verifier.verify_token(token)
