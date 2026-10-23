
"""Inventory department menu for AutoCare."""

from app.cli.navigation import (
    show_menu,
    navigation_action,
)

from app.modules.inventory.inventory_functions import (
    add_spare_part,
    view_inventory,
    restock_part,
    issue_part_to_ticket,
    view_low_stock,
)


def inventory_menu(session, user):
    """Display the Inventory menu."""

    options = {
        "1": "Add Spare Part",
        "2": "View Inventory",
        "3": "Restock Spare Part",
        "4": "Issue Part to Repair Ticket",
        "5": "View Low Stock Alerts",
    }

    actions = {
        "1": add_spare_part,
        "2": view_inventory,
        "3": restock_part,
        "4": issue_part_to_ticket,
        "5": view_low_stock,
    }

    while True:
        choice = show_menu(
            title="AUTOCARE INVENTORY",
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
