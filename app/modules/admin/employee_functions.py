import maskpass

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.auth.passwords import hash_password
from app.auth.permissions import has_permission
from app.auth.user_management import create_employee

from app.database.auth_models import (
    User,
    Role,
    UserRole,
    Permission,
    UserPermissionOverride,
)


def list_employees(session, admin):
    """Display all registered employees and their roles."""

    if not has_permission(session, admin, "users.manage"):
        print("Access denied.")
        return

    users = session.scalars(
        select(User)
        .options(
            selectinload(User.roles).selectinload(UserRole.role)
        )
        .order_by(User.user_id)
    ).all()

    print("\n========== EMPLOYEES ==========")

    if not users:
        print("No employees found.")
        return

    for user in users:
        role_names = [
            assignment.role.role_name
            for assignment in user.roles
        ]

        roles = ", ".join(role_names) or "No roles"
        status = "Active" if user.is_active else "Inactive"

        print(
            f"ID: {user.user_id} | "
            f"Username: {user.username} | "
            f"Roles: {roles} | "
            f"Status: {status}"
        )


def add_employee(session, admin):
    """Create a new employee and assign one or more roles."""

    if not has_permission(session, admin, "users.manage"):
        print("Access denied.")
        return

    print("\n========== CREATE EMPLOYEE ==========")

    username = input("Username: ").strip()

    password = maskpass.askpass(
        prompt="Password: ",
        mask="*"
    )

    confirm_password = maskpass.askpass(
        prompt="Confirm Password: ",
        mask="*"
    )

    if password != confirm_password:
        print("Passwords do not match.")
        return

    roles = session.scalars(
        select(Role).order_by(Role.role_name)
    ).all()

    if not roles:
        print("No roles found. Seed permissions first.")
        return

    print("\nAvailable Roles:")

    for index, role in enumerate(roles, start=1):
        print(f"{index}. {role.role_name}")

    choice = input(
        "\nSelect role numbers (e.g. 2,4): "
    ).strip()

    try:
        selected_numbers = {
            int(number.strip())
            for number in choice.split(",")
        }

        if not selected_numbers or any(
            number < 1 or number > len(roles)
            for number in selected_numbers
        ):
            print("Invalid role selection.")
            return

        selected_roles = [
            roles[number - 1].role_name
            for number in sorted(selected_numbers)
        ]

        print("\nSelected Roles:")

        for role_name in selected_roles:
            print(f"- {role_name}")

        confirm = input(
            "\nCreate employee? (y/N): "
        ).strip().lower()

        if confirm not in ("y", "yes"):
            print("Employee creation cancelled.")
            return

        employee = create_employee(
            session=session,
            acting_user=admin,
            username=username,
            password=password,
            role_names=selected_roles
        )

        session.commit()

        print("\nEmployee created successfully!")
        print(f"Employee ID: {employee.user_id}")
        print(f"Username: {employee.username}")
        print(f"Roles: {', '.join(selected_roles)}")

    except (ValueError, PermissionError) as error:
        session.rollback()
        print(f"Error: {error}")


def edit_employee_roles(session, admin):
    """Edit the roles assigned to an existing employee."""

    if not has_permission(session, admin, "users.manage"):
        print("Access denied.")
        return

    print("\n========== EDIT EMPLOYEE ROLES ==========")

    employee_id = input("Enter Employee ID: ").strip()

    if not employee_id.isdigit():
        print("Invalid Employee ID.")
        return

    employee = session.get(User, int(employee_id))

    if employee is None:
        print("Employee not found.")
        return

    if employee.user_id == admin.user_id:
        print("You cannot change your own roles.")
        return

    current_assignments = session.scalars(
        select(UserRole).where(
            UserRole.user_id == employee.user_id
        )
    ).all()

    current_role_ids = {
        assignment.role_id
        for assignment in current_assignments
    }

    roles = session.scalars(
        select(Role).order_by(Role.role_name)
    ).all()

    if not roles:
        print("No roles available.")
        return

    current_role_names = [
        role.role_name
        for role in roles
        if role.role_id in current_role_ids
    ]

    print(f"\nEmployee: {employee.username}")
    print(
        f"Current Roles: "
        f"{', '.join(current_role_names) or 'No roles'}"
    )

    print("\nAvailable Roles:")

    for index, role in enumerate(roles, start=1):
        print(f"{index}. {role.role_name}")

    choice = input(
        "\nEnter new role numbers (e.g. 2,4): "
    ).strip()

    try:
        selected_numbers = {
            int(number.strip())
            for number in choice.split(",")
        }

        if not selected_numbers or any(
            number < 1 or number > len(roles)
            for number in selected_numbers
        ):
            print("Invalid role selection.")
            return

        selected_role_ids = {
            roles[number - 1].role_id
            for number in selected_numbers
        }

        print("\nNew Roles:")

        for role in roles:
            if role.role_id in selected_role_ids:
                print(f"- {role.role_name}")

        confirm = input(
            "\nSave changes? (y/N): "
        ).strip().lower()

        if confirm not in ("y", "yes"):
            print("Changes cancelled.")
            return

        # Remove roles that are no longer selected.
        for assignment in current_assignments:
            if assignment.role_id not in selected_role_ids:
                session.delete(assignment)

        # Add any newly selected roles.
        for role_id in selected_role_ids - current_role_ids:
            session.add(
                UserRole(
                    user_id=employee.user_id,
                    role_id=role_id
                )
            )

        session.commit()

        print("\nEmployee roles updated successfully!")

    except ValueError:
        session.rollback()
        print("Invalid input. Enter numbers separated by commas.")
def change_employee_status(session, admin):
    """Activate or deactivate an employee account."""

    if not has_permission(session, admin, "users.manage"):
        print("Access denied.")
        return

    print("\n========== EMPLOYEE STATUS ==========")

    employee_id = input("Enter Employee ID: ").strip()

    if not employee_id.isdigit():
        print("Invalid Employee ID.")
        return

    employee = session.get(User, int(employee_id))

    if employee is None:
        print("Employee not found.")
        return

    if employee.user_id == admin.user_id:
        print("You cannot deactivate your own account.")
        return

    # Protect Administrator accounts.
    admin_role = session.scalar(
        select(UserRole)
        .join(Role)
        .where(
            UserRole.user_id == employee.user_id,
            Role.role_name == "Administrator"
        )
    )

    if admin_role is not None:
        print("Administrator accounts cannot be changed here.")
        return

    current_status = "Active" if employee.is_active else "Inactive"

    print(f"\nEmployee: {employee.username}")
    print(f"Current Status: {current_status}")

    if employee.is_active:
        action = "Deactivate"
    else:
        action = "Activate"

    confirm = input(
        f"\n{action} this employee? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Operation cancelled.")
        return

    employee.is_active = not employee.is_active
    session.commit()

    print(f"\nEmployee {action.lower()}d successfully!")
def reset_employee_password(session, admin):
    """Reset an employee's password."""

    if not has_permission(session, admin, "users.manage"):
        print("Access denied.")
        return

    print("\n========== RESET EMPLOYEE PASSWORD ==========")

    employee_id = input("Enter Employee ID: ").strip()

    if not employee_id.isdigit():
        print("Invalid Employee ID.")
        return

    employee = session.get(User, int(employee_id))

    if employee is None:
        print("Employee not found.")
        return

    if employee.user_id == admin.user_id:
        print("Use the account settings to change your own password.")
        return

    print(f"\nEmployee: {employee.username}")

    password = maskpass.askpass(
        prompt="New Password: ",
        mask="*"
    )

    confirm_password = maskpass.askpass(
        prompt="Confirm Password: ",
        mask="*"
    )

    if password != confirm_password:
        print("Passwords do not match.")
        return

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    confirm = input(
        "\nReset employee password? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Password reset cancelled.")
        return

    employee.password_hash = hash_password(password)
    session.commit()

    print("\nPassword reset successfully!")
def delete_employee(session, admin):
    """Permanently delete an employee account."""

    if not has_permission(session, admin, "users.manage"):
        print("Access denied.")
        return

    print("\n========== DELETE EMPLOYEE ==========")

    employee_id = input("Enter Employee ID: ").strip()

    if not employee_id.isdigit():
        print("Invalid Employee ID.")
        return

    employee = session.get(User, int(employee_id))

    if employee is None:
        print("Employee not found.")
        return

    if employee.user_id == admin.user_id:
        print("You cannot delete your own account.")
        return

    admin_role = session.scalar(
        select(UserRole)
        .join(Role)
        .where(
            UserRole.user_id == employee.user_id,
            Role.role_name == "Administrator"
        )
    )

    if admin_role is not None:
        print("Administrator accounts cannot be deleted here.")
        return

    print(f"\nEmployee ID: {employee.user_id}")
    print(f"Username: {employee.username}")

    confirm = input(
        "\nType DELETE to permanently remove this employee: "
    ).strip()

    if confirm != "DELETE":
        print("Deletion cancelled.")
        return

    # Delete individual permission overrides.
    session.execute(
        delete(UserPermissionOverride).where(
            UserPermissionOverride.user_id == employee.user_id
        )
    )

    # Delete role assignments.
    session.execute(
        delete(UserRole).where(
            UserRole.user_id == employee.user_id
        )
    )

    # Delete the user.
    session.delete(employee)
    session.commit()

    print("\nEmployee deleted successfully!")
def manage_employee_permissions(session, admin):
    """Manage individual employee permission overrides."""

    if not has_permission(session, admin, "permissions.manage"):
        print("Access denied.")
        return

    print("\n========== MANAGE PERMISSIONS ==========")

    employee_id = input("Enter Employee ID: ").strip()

    if not employee_id.isdigit():
        print("Invalid Employee ID.")
        return

    employee = session.get(User, int(employee_id))

    if employee is None:
        print("Employee not found.")
        return

    if employee.user_id == admin.user_id:
        print("You cannot override your own permissions here.")
        return

    # Protect Administrator accounts.
    admin_role = session.scalar(
        select(UserRole)
        .join(Role)
        .where(
            UserRole.user_id == employee.user_id,
            Role.role_name == "Administrator"
        )
    )

    if admin_role is not None:
        print("Administrator permissions cannot be changed here.")
        return

    permissions = session.scalars(
        select(Permission).order_by(Permission.permission_name)
    ).all()

    print(f"\nEmployee: {employee.username}")
    print("\nAvailable Permissions:")

    for index, permission in enumerate(permissions, start=1):
        override = session.get(
            UserPermissionOverride,
            (employee.user_id, permission.permission_id)
        )

        if override is None:
            status = "Role default"
        elif override.is_allowed:
            status = "Granted"
        else:
            status = "Denied"

        print(
            f"{index}. {permission.permission_name} "
            f"[{status}]"
        )

    choice = input(
        "\nSelect Permission Number: "
    ).strip()

    if not choice.isdigit():
        print("Invalid selection.")
        return

    index = int(choice)

    if index < 1 or index > len(permissions):
        print("Invalid permission number.")
        return

    selected_permission = permissions[index - 1]

    print(f"\nSelected: {selected_permission.permission_name}")
    print("1. Grant Permission")
    print("2. Deny Permission")
    print("3. Restore Role Default")
    print("0. Cancel")

    action = input("\nSelect an option: ").strip()

    if action not in ("1", "2", "3"):
        print("Operation cancelled.")
        return

    # Ask for confirmation before changing access.
    confirm = input(
        "Save permission change? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Operation cancelled.")
        return

    override = session.get(
        UserPermissionOverride,
        (employee.user_id, selected_permission.permission_id)
    )

    if action == "3":
        if override is not None:
            session.delete(override)

    else:
        is_allowed = action == "1"

        if override is None:
            session.add(
                UserPermissionOverride(
                    user_id=employee.user_id,
                    permission_id=selected_permission.permission_id,
                    is_allowed=is_allowed
                )
            )
        else:
            override.is_allowed = is_allowed

    session.commit()

    print("\nEmployee permission updated successfully!")
