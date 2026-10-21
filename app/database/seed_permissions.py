
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.auth_models import (
    Role,
    Permission,
    RolePermission,
)


PERMISSIONS = {
    "customers.create": "Register a new customer",
    "customers.view": "View customer information",
    "vehicles.create": "Register a new vehicle",
    "vehicles.view": "View vehicle information",
    "repairs.create": "Create repair tickets",
    "repairs.view": "View repair tickets",
    "repairs.assign_mechanic": "Assign mechanics",
    "repairs.update_diagnosis": "Update repair diagnosis",
    "repairs.update_status": "Update repair status",
    "inventory.view": "View spare parts",
    "inventory.manage": "Manage inventory",
    "inventory.issue_parts": "Issue spare parts",
    "invoices.create": "Create invoices",
    "invoices.view": "View invoices",
    "payments.create": "Record payments",
    "payments.view": "View payment history",
    "reports.view": "View reports",
    "users.manage": "Manage user accounts",
    "permissions.manage": "Manage roles and permissions",
}


ROLE_PERMISSIONS = {
    "Reception": [
        "customers.create",
        "customers.view",
        "vehicles.create",
        "vehicles.view",
    ],
    "Service Advisor": [
        "customers.view",
        "vehicles.view",
        "repairs.create",
        "repairs.view",
        "repairs.assign_mechanic",
        "invoices.view",
    ],
    "Mechanic": [
        "repairs.view",
        "repairs.update_diagnosis",
        "repairs.update_status",
        "inventory.view",
    ],
    "Inventory": [
        "inventory.view",
        "inventory.manage",
        "inventory.issue_parts",
        "repairs.view",
    ],
    "Cashier": [
        "customers.view",
        "invoices.view",
        "invoices.create",
        "payments.create",
        "payments.view",
    ],
    "Administrator": list(PERMISSIONS),
}


def seed_permissions():
    """Create initial roles, permissions, and role assignments."""

    with SessionLocal() as session:
        roles = {}
        permissions = {}

        # 1. Create roles if they do not already exist.
        for role_name in ROLE_PERMISSIONS:
            role = session.scalar(
                select(Role).where(Role.role_name == role_name)
            )

            if role is None:
                role = Role(role_name=role_name)
                session.add(role)
                session.flush()

            roles[role_name] = role

        # 2. Create permissions if they do not already exist.
        for permission_name, description in PERMISSIONS.items():
            permission = session.scalar(
                select(Permission).where(
                    Permission.permission_name == permission_name
                )
            )

            if permission is None:
                permission = Permission(
                    permission_name=permission_name,
                    description=description,
                )
                session.add(permission)
                session.flush()

            permissions[permission_name] = permission

        # 3. Assign permissions to the correct roles.
        new_assignments = 0

        for role_name, permission_names in ROLE_PERMISSIONS.items():
            role = roles[role_name]

            for permission_name in permission_names:
                permission = permissions[permission_name]

                existing = session.get(
                    RolePermission,
                    (role.role_id, permission.permission_id)
                )

                if existing is None:
                    session.add(
                        RolePermission(
                            role_id=role.role_id,
                            permission_id=permission.permission_id,
                        )
                    )
                    new_assignments += 1

        session.commit()

        print("\nAutoCare permissions initialized!")
        print(f"Roles configured: {len(roles)}")
        print(f"Permissions configured: {len(permissions)}")
        print(f"New assignments: {new_assignments}")


if __name__ == "__main__":
    seed_permissions()
