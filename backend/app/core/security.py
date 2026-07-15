from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Return a secure password hash."""

    return password_hash.hash(plain_password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Return whether a plaintext password matches a stored hash."""

    try:
        return password_hash.verify(
            plain_password,
            hashed_password,
        )
    except UnknownHashError:
        return False