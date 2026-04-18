import pytest
from clearmetrics.domain.services.auth_service import AuthService
from clearmetrics.ports.outbound.i_token_generator_port import ITokenGeneratorPort
from clearmetrics.ports.outbound.i_token_verifier_port import ITokenVerifierPort


class FakeTokenGenerator(ITokenGeneratorPort):
    def generate_token(self, user_id: str, role: str) -> str:
        return f"fake-token-{user_id}-{role}"


class FakeTokenVerifier(ITokenVerifierPort):
    def verify_token(self, token: str) -> dict[str, str]:
        if token.startswith("fake-token-"):
            remainder = token[len("fake-token-"):]
            user_id, role = remainder.rsplit("-", 1)
            return {"user_id": user_id, "role": role}
        raise ValueError("Invalid token")


class BrokenTokenVerifier(ITokenVerifierPort):
    def verify_token(self, token: str) -> dict[str, str]:
        raise ValueError("Invalid token")


class TestAuthService:
    def test_generate_token_returns_token(self) -> None:
        service = AuthService(
            generator=FakeTokenGenerator(),
            verifier=FakeTokenVerifier(),
        )
        token = service.generate_token(user_id="usr-001", role="admin")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_returns_payload(self) -> None:
        service = AuthService(
            generator=FakeTokenGenerator(),
            verifier=FakeTokenVerifier(),
        )
        token = service.generate_token(user_id="usr-001", role="admin")
        payload = service.verify_token(token)
        assert payload["user_id"] == "usr-001"
        assert payload["role"] == "admin"

    def test_verify_raises_on_invalid_token(self) -> None:
        service = AuthService(
            generator=FakeTokenGenerator(),
            verifier=BrokenTokenVerifier(),
        )
        with pytest.raises(ValueError):
            service.verify_token("invalid-token")

    def test_generate_passes_user_id_and_role(self) -> None:
        received: list[tuple[str, str]] = []

        class CapturingGenerator(ITokenGeneratorPort):
            def generate_token(self, user_id: str, role: str) -> str:
                received.append((user_id, role))
                return "token"

        service = AuthService(generator=CapturingGenerator(), verifier=FakeTokenVerifier())
        service.generate_token(user_id="usr-042", role="analyst")
        assert received[0] == ("usr-042", "analyst")

    def test_verify_passes_token_to_verifier(self) -> None:
        received: list[str] = []

        class CapturingVerifier(ITokenVerifierPort):
            def verify_token(self, token: str) -> dict[str, str]:
                received.append(token)
                return {"user_id": "usr-001", "role": "viewer"}

        service = AuthService(generator=FakeTokenGenerator(), verifier=CapturingVerifier())
        service.verify_token("my-token")
        assert received[0] == "my-token"

    def test_service_depends_on_ports(self) -> None:
        service = AuthService(generator=FakeTokenGenerator(), verifier=FakeTokenVerifier())
        assert isinstance(service._generator, ITokenGeneratorPort)
        assert isinstance(service._verifier, ITokenVerifierPort)
