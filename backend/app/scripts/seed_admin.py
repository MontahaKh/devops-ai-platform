"""Create or promote the configured administrator account."""
import os
import sys

from sqlalchemy import select

from app.core.enums import UserRole
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User


def main() -> int:
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not all((username, email, password)):
        print(
            "ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD are required "
            "when running the admin seed.",
            file=sys.stderr,
        )
        return 2
    if len(password) < 8:
        print("ADMIN_PASSWORD must contain at least 8 characters.", file=sys.stderr)
        return 2

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        email_owner = db.scalar(select(User).where(User.email == email))
        if email_owner and (not user or email_owner.id != user.id):
            print("ADMIN_EMAIL is already used by another account.", file=sys.stderr)
            return 1

        if user is None:
            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
            db.add(user)
            action = "created"
        else:
            user.email = email
            user.hashed_password = hash_password(password)
            user.role = UserRole.ADMIN.value
            user.is_active = True
            action = "updated"

        db.commit()
        print(f"Admin account {action}: {username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
