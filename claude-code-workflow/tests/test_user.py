import pytest

from user import User, is_valid_email


class TestIsValidEmail:
    """Tests for is_valid_email."""

    def test_valid_simple(self):
        """Standard address passes."""
        assert is_valid_email("user@example.com") is True

    def test_valid_subdomains(self):
        """Address with subdomains passes."""
        assert is_valid_email("user@mail.example.co.uk") is True

    def test_valid_plus_tag(self):
        """Plus-tagged local part passes."""
        assert is_valid_email("user+tag@example.com") is True

    def test_valid_leading_whitespace(self):
        """Leading whitespace is stripped before matching."""
        assert is_valid_email("  user@example.com") is True

    def test_valid_trailing_whitespace(self):
        """Trailing whitespace is stripped before matching."""
        assert is_valid_email("user@example.com  ") is True

    def test_invalid_missing_at(self):
        """Address without @ fails."""
        assert is_valid_email("userexample.com") is False

    def test_invalid_missing_tld(self):
        """Address without TLD fails."""
        assert is_valid_email("user@example") is False

    def test_invalid_short_tld(self):
        """Single-character TLD fails."""
        assert is_valid_email("user@example.c") is False

    def test_invalid_empty_string(self):
        """Empty string fails."""
        assert is_valid_email("") is False

    def test_invalid_whitespace_only(self):
        """Whitespace-only string fails."""
        assert is_valid_email("   ") is False

    def test_redos_probe(self, benchmark=None):
        """Long malformed domain must not cause catastrophic backtracking."""
        evil = "a@" + "a" * 50 + "b"
        # Should return quickly and not hang
        assert is_valid_email(evil) is False


class TestUserModel:
    """Tests for the User Pydantic model with EmailStr validation."""

    def test_valid_user(self):
        """User with valid email constructs successfully."""
        u = User(name="Alice", email="alice@example.com")
        assert u.email == "alice@example.com"

    def test_invalid_email_raises(self):
        """User construction fails with an invalid email."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            User(name="Bob", email="not-an-email")
