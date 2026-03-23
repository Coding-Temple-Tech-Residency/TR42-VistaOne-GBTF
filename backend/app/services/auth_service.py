import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(contractor, password: str) -> bool:
    if not contractor.password_hash:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), contractor.password_hash.encode("utf-8"))


def set_password(contractor, password: str) -> None:
    contractor.password_hash = hash_password(password)
