
"""Reception department menu for AutoCare."""

from app.cli.navigation import (
    show_menu,
    navigation_action,
)

from app.modules.reception.reception_functions import (
    register_customer,
    register_vehicle,
    search_customer,
    view_customer_vehicles,
)


def reception_menu(session, user):
    """Display the Reception menu and handle user choices."""

    options = {
        "1": "Register Customer",
        "2": "Register Vehicle",
        "3": "Search Customer",
        "4": "View Customer Vehicles",
    }

    actions = {
        "1": register_customer,
        "2": register_vehicle,
        "3": search_customer,
        "4": view_customer_vehicles,
    }

    while True:
        choice = show_menu(
            title="AUTOCARE RECEPTION",
            options=options,
            username=user.username,
        )

        action = navigation_action(choice)

        if action is not None:
            return action

        selected_function = actions.get(choice)

        if selected_function is None:
            print("\nInvalid option. Please try again.")
            continue

        selected_function(session, user)
