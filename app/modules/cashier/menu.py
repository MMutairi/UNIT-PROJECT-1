
"""Cashier department menu for AutoCare."""

from app.cli.navigation import (
    show_menu,
    navigation_action,
)

from app.modules.cashier.cashier_functions import (
    create_invoice,
    view_invoice,
    record_payment,
    view_unpaid_invoices,
    view_payment_history,
)


def cashier_menu(session, user):
    """Display the Cashier menu."""

    options = {
        "1": "Create Invoice",
        "2": "View Invoice",
        "3": "Record Payment",
        "4": "View Unpaid Invoices",
        "5": "View Payment History",
    }

    actions = {
        "1": create_invoice,
        "2": view_invoice,
        "3": record_payment,
        "4": view_unpaid_invoices,
        "5": view_payment_history,
    }

    while True:
        choice = show_menu(
            title="AUTOCARE CASHIER",
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
