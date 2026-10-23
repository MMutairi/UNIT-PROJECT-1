
"""Service Advisor menu for AutoCare."""

from app.cli.navigation import (
    show_menu,
    navigation_action,
)

from app.modules.service_advisor.advisor_functions import (
    register_mechanic,
    create_repair_ticket,
    assign_mechanic,
    list_repair_tickets,
)


def advisor_menu(session, user):
    """Display the Service Advisor menu."""

    options = {
        "1": "Register Mechanic",
        "2": "Create Repair Ticket",
        "3": "Assign Mechanic",
        "4": "List Repair Tickets",
    }

    actions = {
        "1": register_mechanic,
        "2": create_repair_ticket,
        "3": assign_mechanic,
        "4": list_repair_tickets,
    }

    while True:
        choice = show_menu(
            title="AUTOCARE SERVICE ADVISOR",
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
