import hashlib

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith("$2a$") or stored_hash.startswith("$2b$") or stored_hash.startswith("$2y$"):
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))

    # Backward compatibility for legacy SHA-512 hashes.
    return hashlib.sha512(password.encode("utf-8")).hexdigest() == stored_hash
