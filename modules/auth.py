"""
auth.py
Password hashing and lightweight session helpers. Uses stdlib hashlib
PBKDF2-HMAC-SHA256 with a per-user random salt so the app has zero
fragile third-party crypto dependency (more reliable for Streamlit Cloud
deployment) while still never storing plaintext passwords.
"""
from __future__ import annotations
import hashlib
import hmac
import os
import re
from dataclasses import dataclass

PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Returns 'salt_hex$hash_hex' — safe to store in the database."""
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${pw_hash.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return hmac.compare_digest(candidate, expected)


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class ValidationResult:
    ok: bool
    message: str = ""


def validate_signup(email: str, password: str, confirm_password: str) -> ValidationResult:
    if not email or not EMAIL_RE.match(email):
        return ValidationResult(False, "Please enter a valid email address.")
    if len(password) < 8:
        return ValidationResult(False, "Password must be at least 8 characters long.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return ValidationResult(False, "Password must contain both letters and numbers.")
    if password != confirm_password:
        return ValidationResult(False, "Passwords do not match.")
    return ValidationResult(True)
