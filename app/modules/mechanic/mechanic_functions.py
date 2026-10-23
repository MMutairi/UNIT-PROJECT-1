
"""Core Mechanic functions for AutoCare."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.auth.permissions import has_permission
from app.database.workshop_models import (
    Mechanic,
    RepairTicket,
)


def view_assigned_repairs(session, user):
    """Display repair tickets assigned to a mechanic."""

    if not has_permission(session, user, "repairs.view"):
        print("Access denied.")
        return

    print("\n===== ASSIGNED REPAIRS =====")

    mechanic_id = input("Mechanic ID: ").strip()

    if not mechanic_id.isascii() or not mechanic_id.isdigit():
        print("Invalid Mechanic ID.")
        return

    mechanic = session.get(Mechanic, int(mechanic_id))

    if mechanic is None:
        print("Mechanic not found.")
        return

    tickets = session.scalars(
        select(RepairTicket)
        .where(
            RepairTicket.mechanic_id == mechanic.mechanic_id
        )
        .options(
            selectinload(RepairTicket.vehicle)
        )
        .order_by(RepairTicket.ticket_id)
    ).all()

    print(f"\nMechanic: {mechanic.full_name}")

    if not tickets:
        print("No repair tickets assigned.")
        return

    active_count = 0

    for ticket in tickets:
        if ticket.status not in ("Completed", "Cancelled"):
            active_count += 1

        print("-" * 45)
        print(f"Ticket ID: {ticket.ticket_id}")
        print(
            f"Vehicle: {ticket.vehicle.manufacturer} "
            f"{ticket.vehicle.model}"
        )
        print(f"Plate: {ticket.vehicle.plate_number}")
        print(f"Problem: {ticket.problem_description}")
        print(f"Diagnosis: {ticket.diagnosis or 'Not recorded'}")
        print(f"Status: {ticket.status}")

    print("-" * 45)
    print(f"Total tickets: {len(tickets)}")
    print(f"Active tickets: {active_count}")


def update_diagnosis(session, user):
    """Record or update a repair ticket diagnosis."""

    if not has_permission(
        session, user, "repairs.update_diagnosis"
    ):
        print("Access denied.")
        return

    print("\n===== UPDATE DIAGNOSIS =====")

    ticket_id = input("Repair Ticket ID: ").strip()

    if not ticket_id.isascii() or not ticket_id.isdigit():
        print("Invalid Ticket ID.")
        return

    ticket = session.get(RepairTicket, int(ticket_id))

    if ticket is None:
        print("Repair ticket not found.")
        return

    if ticket.mechanic_id is None:
        print("This ticket has no assigned mechanic.")
        return

    if ticket.status in ("Completed", "Cancelled"):
        print("Cannot modify a closed repair ticket.")
        return

    mechanic = session.get(Mechanic, ticket.mechanic_id)

    if mechanic is None or not mechanic.is_active:
        print("Assigned mechanic is unavailable.")
        return

    print(f"\nTicket ID: {ticket.ticket_id}")
    print(f"Problem: {ticket.problem_description}")
    print(f"Current diagnosis: {ticket.diagnosis or 'None'}")

    diagnosis = input("\nEnter diagnosis: ").strip()

    if not diagnosis or len(diagnosis) > 500:
        print("Diagnosis must contain 1 to 500 characters.")
        return

    confirm = input(
        "\nSave diagnosis? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Update cancelled.")
        return

    try:
        ticket.diagnosis = diagnosis
        session.commit()

        print("\nDiagnosis updated successfully!")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to update diagnosis.")


def update_repair_status(session, user):
    """Update a repair ticket's workflow status."""

    if not has_permission(
        session, user, "repairs.update_status"
    ):
        print("Access denied.")
        return

    print("\n===== UPDATE REPAIR STATUS =====")

    ticket_id = input("Repair Ticket ID: ").strip()

    if not ticket_id.isascii() or not ticket_id.isdigit():
        print("Invalid Ticket ID.")
        return

    ticket = session.get(RepairTicket, int(ticket_id))

    if ticket is None:
        print("Repair ticket not found.")
        return

    if ticket.mechanic_id is None:
        print("Assign a mechanic before updating the status.")
        return

    mechanic = session.get(Mechanic, ticket.mechanic_id)

    if mechanic is None or not mechanic.is_active:
        print("Assigned mechanic is unavailable.")
        return

    print(f"\nTicket ID: {ticket.ticket_id}")
    print(f"Current Status: {ticket.status}")

    if ticket.status == "Pending":
        new_status = "In Progress"

    elif ticket.status == "In Progress":
        if not ticket.diagnosis:
            print("Record a diagnosis before completing the repair.")
            return

        new_status = "Completed"

    else:
        print("No further status changes allowed for this ticket.")
        return

    print(f"Next Status: {new_status}")

    confirm = input(
        "\nConfirm status update? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Status update cancelled.")
        return

    try:
        ticket.status = new_status
        session.commit()

        print(f"\nRepair status updated to: {new_status}")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to update repair status.")
