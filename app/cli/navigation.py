BACK = "back"
LOGOUT = "logout"


def show_menu(
    title: str,
    options: dict[str, str],
    username: str | None = None,
    back_label: str | None = "Back to Departments",
) -> str:
    """Display a menu and return the selected option."""

    print("\n" + "=" * 45)
    print(f"{title:^45}")
    print("=" * 45)

    if username:
        print(f"Logged in as: {username}")
        print("-" * 45)

    for number, description in options.items():
        print(f"{number}. {description}")

    if back_label is not None:
        print(f"8. {back_label}")

    print("0. Logout")
    print("-" * 45)

    return input("Select an option: ").strip()


def navigation_action(choice: str) -> str | None:
    """Return the navigation action, if any."""

    if choice == "8":
        return BACK

    if choice == "0":
        return LOGOUT

    return None
