
"""Mechanic department menu for AutoCare."""

from app.cli.navigation import (
    show_menu,
    navigation_action,
)

from app.modules.mechanic.mechanic_functions import (
    view_assigned_repairs,
    update_diagnosis,
    update_repair_status,
)


def mechanic_menu(session, user):
    """Display the Mechanic menu."""

    options = {
        "1": "View Assigned Repairs",
        "2": "Update Diagnosis",
        "3": "Update Repair Status",
    }

    actions = {
        "1": view_assigned_repairs,
        "2": update_diagnosis,
        "3": update_repair_status,
    }

    while True:
        choice = show_menu(
            title="AUTOCARE MECHANIC",
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
