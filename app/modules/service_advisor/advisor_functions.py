
"""Core Service Advisor functions for AutoCare."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.auth.permissions import has_permission
from app.database.workshop_models import (
    Vehicle,
    Mechanic,
    RepairTicket,
)


def register_mechanic(session, user):
    """Register a mechanic in the workshop roster."""

    if not has_permission(
        session, user, "repairs.assign_mechanic"
    ):
        print("Access denied.")
        return

    print("\n===== REGISTER MECHANIC =====")

    full_name = input("Mechanic name: ").strip()
    specialty = input("Specialty: ").strip()

    if not full_name or len(full_name) > 100:
        print("Invalid mechanic name.")
        return

    if not specialty or len(specialty) > 50:
        print("Invalid specialty.")
        return

    mechanic = Mechanic(
        full_name=full_name,
        specialty=specialty,
        is_active=True,
    )

    try:
        session.add(mechanic)
        session.commit()
        print(f"Mechanic registered! ID: {mechanic.mechanic_id}")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to register mechanic.")


def create_repair_ticket(session, user):
    """Create a repair ticket for an existing vehicle."""

    if not has_permission(
        session, user, "repairs.create"
    ):
        print("Access denied.")
        return

    print("\n===== CREATE REPAIR TICKET =====")

    vehicle_id = input("Vehicle ID: ").strip()

    if not vehicle_id.isascii() or not vehicle_id.isdigit():
        print("Invalid Vehicle ID.")
        return

    vehicle = session.get(Vehicle, int(vehicle_id))

    if vehicle is None:
        print("Vehicle not found.")
        return

    print(
        f"Vehicle: {vehicle.manufacturer} "
        f"{vehicle.model} ({vehicle.plate_number})"
    )

    problem = input("Describe the problem: ").strip()

    if not problem or len(problem) > 255:
        print("Description must contain 1 to 255 characters.")
        return

    ticket = RepairTicket(
        vehicle_id=vehicle.vehicle_id,
        mechanic_id=None,
        problem_description=problem,
        status="Pending",
    )

    try:
        session.add(ticket)
        session.commit()

        print("\nRepair ticket created!")
        print(f"Ticket ID: {ticket.ticket_id}")
        print(f"Vehicle ID: {ticket.vehicle_id}")
        print(f"Status: {ticket.status}")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to create repair ticket.")


def assign_mechanic(session, user):
    """Assign an active mechanic to a repair ticket."""

    if not has_permission(
        session, user, "repairs.assign_mechanic"
    ):
        print("Access denied.")
        return

    print("\n===== ASSIGN MECHANIC =====")

    ticket_id = input("Repair Ticket ID: ").strip()

    if not ticket_id.isascii() or not ticket_id.isdigit():
        print("Invalid Ticket ID.")
        return

    ticket = session.get(RepairTicket, int(ticket_id))

    if ticket is None:
        print("Repair ticket not found.")
        return

    if ticket.status in ("Completed", "Cancelled"):
        print("Cannot assign a mechanic to a closed ticket.")
        return

    mechanics = session.scalars(
        select(Mechanic)
        .where(Mechanic.is_active.is_(True))
        .order_by(Mechanic.mechanic_id)
    ).all()

    if not mechanics:
        print("No active mechanics available.")
        return

    print("\nAvailable Mechanics:")

    for mechanic in mechanics:
        print(
            f"ID: {mechanic.mechanic_id} | "
            f"Name: {mechanic.full_name} | "
            f"Specialty: {mechanic.specialty}"
        )

    mechanic_id = input("\nMechanic ID: ").strip()

    if not mechanic_id.isascii() or not mechanic_id.isdigit():
        print("Invalid Mechanic ID.")
        return

    mechanic = session.get(Mechanic, int(mechanic_id))

    if mechanic is None or not mechanic.is_active:
        print("Mechanic not found or inactive.")
        return

    confirm = input(
        f"Assign {mechanic.full_name} to ticket "
        f"{ticket.ticket_id}? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Assignment cancelled.")
        return

    try:
        ticket.mechanic_id = mechanic.mechanic_id
        session.commit()

        print("\nMechanic assigned successfully!")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to assign mechanic.")


def list_repair_tickets(session, user):
    """Display existing repair tickets."""

    if not has_permission(
        session, user, "repairs.view"
    ):
        print("Access denied.")
        return

    tickets = session.scalars(
        select(RepairTicket)
        .options(
            selectinload(RepairTicket.vehicle),
            selectinload(RepairTicket.mechanic),
        )
        .order_by(RepairTicket.ticket_id)
    ).all()

    print("\n===== REPAIR TICKETS =====")

    if not tickets:
        print("No repair tickets found.")
        return

    for ticket in tickets:
        mechanic_name = (
            ticket.mechanic.full_name
            if ticket.mechanic
            else "Not assigned"
        )

        vehicle_name = (
            f"{ticket.vehicle.manufacturer} "
            f"{ticket.vehicle.model}"
        )

        print("-" * 45)
        print(f"Ticket ID: {ticket.ticket_id}")
        print(f"Vehicle: {vehicle_name}")
        print(f"Problem: {ticket.problem_description}")
        print(f"Mechanic: {mechanic_name}")
        print(f"Status: {ticket.status}")

    print("-" * 45)
