from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password before saving it to the database."""
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hasher.verify(password, stored_hash)