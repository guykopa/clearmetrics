import pytest
from clearmetrics.domain.models.quality_result import QualityResult


class TestQualityResultCreation:
    def test_creates_passing_result(self) -> None:
        result = QualityResult(
            rule_name="NotNullRule",
            passed=True,
            failed_count=0,
            error_samples=[],
        )
        assert result.rule_name == "NotNullRule"
        assert result.passed is True
        assert result.failed_count == 0
        assert result.error_samples == []

    def test_creates_failing_result(self) -> None:
        result = QualityResult(
            rule_name="PositiveAmountRule",
            passed=False,
            failed_count=3,
            error_samples=[{"id": "txn-001", "amount": -5.0}],
        )
        assert result.passed is False
        assert result.failed_count == 3
        assert len(result.error_samples) == 1

    def test_result_is_immutable(self) -> None:
        result = QualityResult(
            rule_name="NotNullRule",
            passed=True,
            failed_count=0,
            error_samples=[],
        )
        with pytest.raises(Exception):
            result.passed = False  # type: ignore[misc]

    def test_raises_on_empty_rule_name(self) -> None:
        with pytest.raises(ValueError):
            QualityResult(
                rule_name="",
                passed=True,
                failed_count=0,
                error_samples=[],
            )

    def test_raises_on_negative_failed_count(self) -> None:
        with pytest.raises(ValueError):
            QualityResult(
                rule_name="NotNullRule",
                passed=False,
                failed_count=-1,
                error_samples=[],
            )

    def test_raises_when_passed_but_failed_count_nonzero(self) -> None:
        with pytest.raises(ValueError):
            QualityResult(
                rule_name="NotNullRule",
                passed=True,
                failed_count=2,
                error_samples=[],
            )

    def test_raises_when_failed_but_failed_count_zero(self) -> None:
        with pytest.raises(ValueError):
            QualityResult(
                rule_name="NotNullRule",
                passed=False,
                failed_count=0,
                error_samples=[],
            )
