
import maskpass
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.passwords import verify_password
from app.database.auth_models import User
from app.database.connection import SessionLocal
def authenticate_user(
    session: Session,
    username: str,
    password: str
) -> User | None:
    """Authenticate a user using their username and password."""

    user = session.scalar(
        select(User).where(User.username == username.strip())
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

def main():

    print("\n===== AUTOCARE LOGIN =====")

    username = input("Username: ").strip()

    show_password = input(
        "Do you want to show your password? (y/n): "
    ).strip().lower()

    if show_password in ("y", "yes"):
        password = input("Password: ")
    else:
        password = maskpass.askpass(
            prompt="Password: ",
            mask="*"
        )

    with SessionLocal() as session:
        user = authenticate_user(session, username, password)

        if user is None:
            print("\nInvalid username, password, or inactive account.")
            return

        print("\nLogin successful!")
        print(f"Welcome, {user.username}!")

        role_names = [
            user_role.role.role_name
            for user_role in user.roles
        ]

        if role_names:
            print(f"Your roles: {', '.join(role_names)}")
        else:
            print("No roles assigned to this account.")



if __name__ == "__main__":
    main()
