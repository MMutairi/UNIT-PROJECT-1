
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.auth_models import (
    User,
    Permission,
    UserRole,
    RolePermission,
    UserPermissionOverride,
)

def has_permission(
    session: Session,
    user: User,
    permission_name: str
) -> bool:

    if not user.is_active:
        return False

    override = session.scalar(
        select(UserPermissionOverride.is_allowed)
        .join(
            Permission,
            UserPermissionOverride.permission_id
            == Permission.permission_id
        )
        .where(
            UserPermissionOverride.user_id == user.user_id,
            Permission.permission_name == permission_name
        )
    )

    if override is not None:
        return override

    role_permission = session.scalar(
        select(RolePermission.permission_id)
        .join(
            Permission,
            RolePermission.permission_id
            == Permission.permission_id
        )
        .join(
            UserRole,
            RolePermission.role_id == UserRole.role_id
        )
        .where(
            UserRole.user_id == user.user_id,
            Permission.permission_name == permission_name
        )
        .limit(1)
    )

    return role_permission is not None
