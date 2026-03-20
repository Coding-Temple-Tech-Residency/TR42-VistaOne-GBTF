from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="scrypt")


def verify_password(contractor, password: str) -> bool:
    return check_password_hash(contractor.password_hash, password)


def set_password(contractor, password: str) -> None:
    contractor.password_hash = generate_password_hash(password, method="scrypt")
