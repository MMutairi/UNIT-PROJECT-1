
import maskpass
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
    """Display the Administrator menu and handle user choices."""

    while True:
        print("\n" + "=" * 45)
        print("       AUTOCARE ADMINISTRATOR MENU")
        print("=" * 45)

        print(f"Logged in as: {admin.username}")
        print("-" * 45)

        print("1. Create Employee")
        print("2. List Employees")
        print("3. Edit Employee Roles")
        print("4. Activate / Deactivate Employee")
        print("5. Reset Employee Password")
        print("6. Delete Employee")
        print("7. Manage Employee Permissions")
        print("0. Logout")

        print("-" * 45)

        choice = input("Select an option: ").strip()

        if choice == "1":
            add_employee(session, admin)

        elif choice == "2":
            list_employees(session, admin)

        elif choice == "3":
            edit_employee_roles(session, admin)

        elif choice == "4":
            change_employee_status(session, admin)

        elif choice == "5":
            reset_employee_password(session, admin)

        elif choice == "6":
            delete_employee(session, admin)

        elif choice == "7":
            manage_employee_permissions(session, admin)

        elif choice == "0":
            print("\nLogged out successfully.")
            break

        else:
            print("\nInvalid option. Please try again.")


def main():
    """Authenticate an authorized user and open the Admin menu."""

    print("\n" + "=" * 45)
    print("             AUTOCARE LOGIN")
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
        admin = authenticate_user(
            session,
            username,
            password
        )

        if admin is None:
            print(
                "\nInvalid username, password, "
                "or inactive account."
            )
            return

        if not has_permission(
            session,
            admin,
            "users.manage"
        ):
            print("\nAccess denied.")
            print(
                "You do not have permission "
                "to access the Administrator menu."
            )
            return

        print(f"\nWelcome back, {admin.username}!")

        admin_menu(session, admin)
if __name__ == "__main__":
    main()
