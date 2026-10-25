
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password
from app.auth.permissions import has_permission
from app.database.auth_models import User, Role, UserRole


def create_employee(
    session: Session,
    acting_user: User,
    username: str,
    password: str,
    role_names: list[str]
) -> User:
    """Create an employee and assign their roles."""

    # Check administrator permission.
    if not has_permission(session, acting_user, "users.manage"):
        raise PermissionError(
            "You do not have permission to manage users."
        )

    username = username.strip()

    if not username:
        raise ValueError("Username cannot be empty.")

    if len(username) > 50:
        raise ValueError("Username is too long.")

    if len(password) < 12:
        raise ValueError(
            "Password must contain at least 12 characters."
        )

    if not role_names:
        raise ValueError("At least one role is required.")

    # Prevent duplicate usernames.
    existing_user = session.scalar(
        select(User).where(User.username == username)
    )

    if existing_user:
        raise ValueError("Username already exists.")

    # Check that all requested roles exist.
    requested_roles = set(role_names)

    roles = session.scalars(
        select(Role).where(Role.role_name.in_(requested_roles))
    ).all()

    found_roles = {role.role_name for role in roles}

    if found_roles != requested_roles:
        missing = requested_roles - found_roles
        raise ValueError(
            f"Unknown roles: {', '.join(sorted(missing))}"
        )

    # Create the employee account.
    employee = User(
        username=username,
        password_hash=hash_password(password),
        is_active=True
    )

    session.add(employee)
    session.flush()

    # Assign employee roles.
    for role in roles:
        session.add(
            UserRole(
                user_id=employee.user_id,
                role_id=role.role_id
            )
        )

    session.flush()

    return employee
