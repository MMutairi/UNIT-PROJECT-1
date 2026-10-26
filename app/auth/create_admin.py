from app.auth.password_input import ask_password
from sqlalchemy import select
from app.auth.passwords import hash_password
from app.database.connection import SessionLocal
from app.database.auth_models import User, Role, UserRole

def create_admin():
    """Create the first administrator account."""

    with SessionLocal() as session:
        # Check whether an administrator already exists.
        existing_admin = session.scalar(
            select(User)
            .join(UserRole, User.user_id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.role_id)
            .where(Role.role_name == "Administrator")
        )

        if existing_admin:
            print("An administrator account already exists.")
            return

        print("\n=== CREATE ADMINISTRATOR ===")

        username = input("Username: ").strip()

        if not username:
            print("Username cannot be empty.")
            return

        existing_user = session.scalar(
            select(User).where(User.username == username)
        )

        if existing_user:
            print("Username already exists.")
            return

        password = ask_password("Password: ")
        confirm_password = ask_password("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match.")
            return

        if len(password) < 12:
            print("Password must contain at least 12 characters.")
            return

        # Hash the password before saving it.
        hashed_password = hash_password(password)

        # Find or create the Administrator role.
        admin_role = session.scalar(
            select(Role).where(Role.role_name == "Administrator")
        )

        if admin_role is None:
            admin_role = Role(role_name="Administrator")
            session.add(admin_role)
            session.flush()

        # Create the administrator user.
        admin_user = User(
            username=username,
            password_hash=hashed_password,
            is_active=True
        )

        session.add(admin_user)
        session.flush()

        # Assign the Administrator role.
        session.add(
            UserRole(
                user_id=admin_user.user_id,
                role_id=admin_role.role_id
            )
        )

        session.commit()

        print("\nAdministrator created successfully!")


if __name__ == "__main__":
    create_admin()
