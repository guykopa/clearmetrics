class DomainException(Exception):
    """Base class for all domain exceptions."""


class InvalidAmountError(DomainException):
    """Raised when a transaction amount is invalid."""


class InvalidCurrencyError(DomainException):
    """Raised when a currency code is not ISO 4217 compliant."""


class InvalidTransactionError(DomainException):
    """Raised when a transaction violates domain invariants."""


class InvalidUserRoleError(DomainException):
    """Raised when an unknown user role is assigned."""


class DuplicateTransactionError(DomainException):
    """Raised when a duplicate transaction id is detected."""


class InvalidDateRangeError(DomainException):
    """Raised when a timestamp falls outside the acceptable range."""
