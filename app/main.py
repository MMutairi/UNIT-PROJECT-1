
"""Main entry point for AutoCare Workshop Management System."""

import maskpass

from app.auth.login import authenticate_user
from app.database.connection import SessionLocal

from app.cli.navigation import (
    show_menu,
    BACK,
    LOGOUT,
)

from app.modules.admin.menu import admin_menu
from app.modules.reception.menu import reception_menu
from app.modules.service_advisor.menu import advisor_menu
from app.modules.mechanic.menu import mechanic_menu
from app.modules.inventory.menu import inventory_menu
from app.modules.cashier.menu import cashier_menu


# All available departments and their menu functions.
DEPARTMENT_MENUS = {
    "Administrator": admin_menu,
    "Reception": reception_menu,
    "Service Advisor": advisor_menu,
    "Mechanic": mechanic_menu,
    "Inventory": inventory_menu,
    "Cashier": cashier_menu,
}


def get_user_departments(user):
    """Get departments assigned to the logged-in user."""

    assigned_roles = {
        assignment.role.role_name
        for assignment in user.roles
    }

    return [
        department
        for department in DEPARTMENT_MENUS
        if department in assigned_roles
    ]


def open_department(session, user, department):
    """Open an authorized department menu."""

    if not user.is_active:
        print("\nYour account is inactive.")
        return LOGOUT

    allowed_departments = get_user_departments(user)

    if department not in allowed_departments:
        print("\nAccess denied: Department not assigned.")
        return BACK

    selected_menu = DEPARTMENT_MENUS.get(department)

    if selected_menu is None:
        print("\nDepartment not available.")
        return BACK

    return selected_menu(session, user)


def department_menu(session, user):
    """Allow employees to navigate between their departments."""

    while True:

        if not user.is_active:
            print("\nYour account is inactive. Logging out.")
            return LOGOUT

        departments = get_user_departments(user)

        if not departments:
            print("\nNo departments assigned to your account.")
            return LOGOUT

        options = {
            str(index): department
            for index, department in enumerate(
                departments,
                start=1
            )
        }

        choice = show_menu(
            title="AUTOCARE DEPARTMENTS",
            options=options,
            username=user.username,
            back_label=None,
        )

        if choice == "0":
            print("\nLogged out successfully.")
            return LOGOUT

        selected_department = options.get(choice)

        if selected_department is None:
            print("\nInvalid department selection.")
            continue

        result = open_department(
            session,
            user,
            selected_department
        )

        if result == LOGOUT:
            print("\nLogged out successfully.")
            return LOGOUT

        # BACK returns the employee to department selection.


def main():
    """Start AutoCare and authenticate the employee."""

    print("\n" + "=" * 45)
    print("       AUTOCARE WORKSHOP SYSTEM")
    print("=" * 45)

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

        user = authenticate_user(
            session,
            username,
            password
        )

        if user is None:
            print(
                "\nInvalid username, password, "
                "or inactive account."
            )
            return

        print("\nLogin successful!")
        print(f"Welcome to AutoCare, {user.username}!")

        department_menu(session, user)


if __name__ == "__main__":
    main()
