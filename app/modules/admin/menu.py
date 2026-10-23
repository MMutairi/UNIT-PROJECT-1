import maskpass
from app.cli.navigation import (
    show_menu,
    navigation_action,
    BACK,
    LOGOUT,
)
from app.auth.login import authenticate_user
from app.auth.permissions import has_permission
from app.database.connection import SessionLocal

from app.modules.admin.employee_functions import (
    add_employee,
    list_employees,
    edit_employee_roles,
    change_employee_status,
    reset_employee_password,
    delete_employee,
    manage_employee_permissions,
)

def admin_menu(session, admin):
    """Display the Administrator menu."""

    options = {
        "1": "Create Employee",
        "2": "List Employees",
        "3": "Edit Employee Roles",
        "4": "Activate / Deactivate Employee",
        "5": "Reset Employee Password",
        "6": "Delete Employee",
        "7": "Manage Employee Permissions",
    }

    actions = {
        "1": add_employee,
        "2": list_employees,
        "3": edit_employee_roles,
        "4": change_employee_status,
        "5": reset_employee_password,
        "6": delete_employee,
        "7": manage_employee_permissions,
    }

    while True:
        choice = show_menu(
            title="AUTOCARE ADMINISTRATOR",
            options=options,
            username=admin.username,
        )

        action = navigation_action(choice)

        if action == BACK:
            print("\nReturning to Departments...")
            return BACK

        if action == LOGOUT:
            return LOGOUT

        selected_function = actions.get(choice)

        if selected_function is None:
            print("\nInvalid option. Please try again.")
            continue

        selected_function(session, admin)

def main():
    """Run the Administrator menu independently."""

    print("\n========== AUTOCARE ADMIN LOGIN ==========")

    username = input("Username: ").strip()

    show_password = input(
        "Do you want to show your password? (y/N): "
    ).strip().lower()

    if show_password in ("y", "yes"):
        password = input("Password: ")
    else:
        password = maskpass.askpass(
            prompt="Password: ",
            mask="*"
        )

    with SessionLocal() as session:
        admin = authenticate_user(
            session,
            username,
            password
        )

        if admin is None:
            print("\nInvalid credentials or inactive account.")
            return

        if not has_permission(session, admin, "users.manage"):
            print("\nAccess denied.")
            return

        result = admin_menu(session, admin)

        if result == "logout":
            print("\nLogged out successfully.")
        else:
            print("\nAdministrator menu closed.")


if __name__ == "__main__":
    main()
