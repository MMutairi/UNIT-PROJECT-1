"""Mechanic department: login-linked, assignment-scoped repair access."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.auth.permissions import has_permission
from app.database.auth_models import MechanicAccount
from app.database.workshop_models import Mechanic, RepairTicket


def get_current_mechanic(session, user):
    """Get the active mechanic connected to the current login."""
    if not user.is_active:
        print("Access denied: inactive employee account.")
        return None
    mapping = session.get(MechanicAccount, user.user_id)
    if mapping is None:
        print("No mechanic record is linked to your login. Contact Administrator.")
        return None
    mechanic = session.get(Mechanic, mapping.mechanic_id)
    if mechanic is None or not mechanic.is_active:
        print("Your mechanic record is inactive or unavailable.")
        return None
    return mechanic


def get_owned_ticket(session, user, ticket_id):
    """Restrict ticket access to the mechanic mapped to the logged-in account."""
    mechanic = get_current_mechanic(session, user)
    if mechanic is None:
        return None
    ticket = session.scalar(
        select(RepairTicket).where(
            RepairTicket.ticket_id == ticket_id,
            RepairTicket.mechanic_id == mechanic.mechanic_id,
        )
    )
    if ticket is None:
        print("Ticket not found or not assigned to your account.")
    return ticket


def _read_ticket_id():
    answer = input("Repair Ticket ID: ").strip()
    if not answer.isascii() or not answer.isdigit() or int(answer) <= 0:
        print("Invalid Ticket ID.")
        return None
    return int(answer)


def view_assigned_repairs(session, user):
    if not has_permission(session, user, "repairs.view"):
        print("Access denied.")
        return
    mechanic = get_current_mechanic(session, user)
    if mechanic is None:
        return
    tickets = session.scalars(
        select(RepairTicket)
        .where(RepairTicket.mechanic_id == mechanic.mechanic_id)
        .options(selectinload(RepairTicket.vehicle))
        .order_by(RepairTicket.ticket_id)
    ).all()
    print(f"\n===== ASSIGNED REPAIRS: {mechanic.full_name} =====")
    if not tickets:
        print("No assigned repair tickets.")
        return
    active = 0
    for ticket in tickets:
        active += ticket.status not in ("Completed", "Cancelled")
        print("-" * 45)
        print(f"Ticket ID: {ticket.ticket_id}")
        print(f"Vehicle: {ticket.vehicle.manufacturer} {ticket.vehicle.model}")
        print(f"Plate: {ticket.vehicle.plate_number}")
        print(f"Problem: {ticket.problem_description}")
        print(f"Diagnosis: {ticket.diagnosis or 'Not recorded'}")
        print(f"Status: {ticket.status}")
    print(f"Total tickets: {len(tickets)} | Active: {active}")


def update_diagnosis(session, user):
    if not has_permission(session, user, "repairs.update_diagnosis"):
        print("Access denied.")
        return
    print("\n===== UPDATE DIAGNOSIS =====")
    ticket_id = _read_ticket_id()
    if ticket_id is None:
        return
    ticket = get_owned_ticket(session, user, ticket_id)
    if ticket is None:
        return
    if ticket.status in ("Completed", "Cancelled"):
        print("Cannot modify a closed repair ticket.")
        return
    print(f"Problem: {ticket.problem_description}")
    print(f"Previous diagnosis: {ticket.diagnosis or 'None'}")
    diagnosis = input("Diagnosis: ").strip()
    if not 1 <= len(diagnosis) <= 500:
        print("Diagnosis must be 1 to 500 characters.")
        return
    if input("Save diagnosis? (y/N): ").strip().lower() not in ("y", "yes"):
        print("Cancelled.")
        return
    try:
        ticket.diagnosis = diagnosis
        session.commit()
        print("Diagnosis saved.")
    except SQLAlchemyError:
        session.rollback()
        print("Failed to update diagnosis.")


def update_repair_status(session, user):
    if not has_permission(session, user, "repairs.update_status"):
        print("Access denied.")
        return
    print("\n===== UPDATE REPAIR STATUS =====")
    ticket_id = _read_ticket_id()
    if ticket_id is None:
        return
    ticket = get_owned_ticket(session, user, ticket_id)
    if ticket is None:
        return
    if ticket.status == "Pending":
        next_status = "In Progress"
    elif ticket.status == "In Progress":
        if not ticket.diagnosis:
            print("Record a diagnosis before completing the repair.")
            return
        next_status = "Completed"
    else:
        print("No further status change is allowed.")
        return
    print(f"Ticket {ticket.ticket_id}: {ticket.status} -> {next_status}")
    if input("Confirm status update? (y/N): ").strip().lower() not in ("y", "yes"):
        print("Cancelled.")
        return
    try:
        ticket.status = next_status
        session.commit()
        print(f"Repair status updated: {next_status}")
    except SQLAlchemyError:
        session.rollback()
        print("Failed to update repair status.")
