
"""Core Inventory functions for AutoCare."""

from decimal import Decimal, InvalidOperation

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from app.auth.permissions import has_permission
from app.database.workshop_models import (
    SparePart,
    RepairPart,
    RepairTicket,
)


def read_positive_int(prompt):
    """Read a positive integer or return None."""
    value = input(prompt).strip()

    if not value.isascii() or not value.isdigit():
        print("Please enter a valid positive number.")
        return None

    number = int(value)

    if number <= 0:
        print("Number must be greater than zero.")
        return None

    return number


def read_price(prompt):
    """Read a nonnegative monetary value with two decimals."""
    raw_value = input(prompt).strip()

    try:
        price = Decimal(raw_value)

        if not price.is_finite():
            raise ValueError

        if price < 0 or price >= Decimal("100000000"):
            raise ValueError

        if price != price.quantize(Decimal("0.01")):
            raise ValueError

        return price

    except (InvalidOperation, ValueError):
        print("Invalid price. Use a valid amount with up to 2 decimals.")
        return None


def add_spare_part(session, user):
    """Register a new spare part in inventory."""

    if not has_permission(session, user, "inventory.manage"):
        print("Access denied.")
        return

    print("\n===== ADD SPARE PART =====")

    part_name = input("Part Name: ").strip()
    part_number = input("Part Number: ").strip().upper()

    if not part_name or len(part_name) > 100:
        print("Part name must contain 1 to 100 characters.")
        return

    if not part_number or len(part_number) > 50:
        print("Part number must contain 1 to 50 characters.")
        return

    existing_part = session.scalar(
        select(SparePart).where(
            SparePart.part_number == part_number
        )
    )

    if existing_part is not None:
        print("This part number already exists.")
        return

    unit_price = read_price("Unit Price (SAR): ")

    if unit_price is None:
        return

    stock_quantity = input("Initial Stock Quantity: ").strip()
    minimum_stock = input("Minimum Stock Level: ").strip()

    if not (
        stock_quantity.isascii()
        and stock_quantity.isdigit()
        and minimum_stock.isascii()
        and minimum_stock.isdigit()
    ):
        print("Stock quantities must be nonnegative integers.")
        return

    spare_part = SparePart(
        part_name=part_name,
        part_number=part_number,
        unit_price=unit_price,
        stock_quantity=int(stock_quantity),
        minimum_stock=int(minimum_stock),
    )

    try:
        session.add(spare_part)
        session.commit()

        print("\nSpare part registered successfully!")
        print(f"Part ID: {spare_part.part_id}")
        print(f"Part: {spare_part.part_name}")
        print(f"Stock: {spare_part.stock_quantity}")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to register spare part.")


def view_inventory(session, user):
    """Display all registered spare parts."""

    if not has_permission(session, user, "inventory.view"):
        print("Access denied.")
        return

    print("\n===== INVENTORY =====")

    parts = session.scalars(
        select(SparePart).order_by(SparePart.part_id)
    ).all()

    if not parts:
        print("Inventory is empty.")
        return

    for part in parts:
        if part.stock_quantity == 0:
            status = "OUT OF STOCK"
        elif part.stock_quantity <= part.minimum_stock:
            status = "LOW STOCK"
        else:
            status = "AVAILABLE"

        print("-" * 50)
        print(f"Part ID: {part.part_id}")
        print(f"Name: {part.part_name}")
        print(f"Part Number: {part.part_number}")
        print(f"Unit Price: {part.unit_price:.2f} SAR")
        print(f"Stock: {part.stock_quantity}")
        print(f"Minimum Stock: {part.minimum_stock}")
        print(f"Status: {status}")

    print("-" * 50)


def restock_part(session, user):
    """Add inventory stock to an existing spare part."""

    if not has_permission(session, user, "inventory.manage"):
        print("Access denied.")
        return

    print("\n===== RESTOCK SPARE PART =====")

    part_id = read_positive_int("Part ID: ")

    if part_id is None:
        return

    part = session.get(SparePart, part_id)

    if part is None:
        print("Spare part not found.")
        return

    print(f"\nPart: {part.part_name}")
    print(f"Current Stock: {part.stock_quantity}")

    quantity = read_positive_int("Quantity to Add: ")

    if quantity is None:
        return

    confirm = input(
        f"Add {quantity} units? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Restock cancelled.")
        return

    try:
        session.execute(
            update(SparePart)
            .where(SparePart.part_id == part_id)
            .values(
                stock_quantity=SparePart.stock_quantity + quantity
            )
        )

        session.commit()
        session.refresh(part)

        print("\nStock updated successfully!")
        print(f"New Stock: {part.stock_quantity}")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to update stock.")


def issue_part_to_ticket(session, user):
    """Issue a spare part to an existing repair ticket."""

    if not has_permission(
        session, user, "inventory.issue_parts"
    ):
        print("Access denied.")
        return

    print("\n===== ISSUE SPARE PART =====")

    ticket_id = read_positive_int("Repair Ticket ID: ")

    if ticket_id is None:
        return

    ticket = session.get(RepairTicket, ticket_id)

    if ticket is None:
        print("Repair ticket not found.")
        return

    if ticket.status in ("Completed", "Cancelled"):
        print("Cannot issue parts to a closed repair ticket.")
        return

    part_id = read_positive_int("Spare Part ID: ")

    if part_id is None:
        return

    part = session.get(SparePart, part_id)

    if part is None:
        print("Spare part not found.")
        return

    print(f"\nPart: {part.part_name}")
    print(f"Available Stock: {part.stock_quantity}")
    print(f"Unit Price: {part.unit_price:.2f} SAR")

    quantity = read_positive_int("Quantity Required: ")

    if quantity is None:
        return

    if quantity > part.stock_quantity:
        print("Insufficient stock.")
        return

    line_total = part.unit_price * quantity

    print(f"\nTicket ID: {ticket.ticket_id}")
    print(f"Quantity: {quantity}")
    print(f"Total Parts Cost: {line_total:.2f} SAR")

    confirm = input(
        "\nConfirm issuing parts? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Operation cancelled.")
        return

    try:
        # Decrease stock only if enough remains.
        result = session.execute(
            update(SparePart)
            .where(
                SparePart.part_id == part_id,
                SparePart.stock_quantity >= quantity,
            )
            .values(
                stock_quantity=SparePart.stock_quantity - quantity
            )
        )

        if result.rowcount != 1:
            session.rollback()
            print("Insufficient stock. Please refresh inventory.")
            return

        # Record the issued parts against the repair ticket.
        repair_part = RepairPart(
            ticket_id=ticket.ticket_id,
            part_id=part.part_id,
            quantity=quantity,
            unit_price=part.unit_price,
        )

        session.add(repair_part)
        session.commit()

        print("\nSpare part issued successfully!")
        print(f"Repair Ticket: {ticket.ticket_id}")
        print(f"Quantity Issued: {quantity}")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to issue spare part.")


def view_low_stock(session, user):
    """Display spare parts at or below minimum stock."""

    if not has_permission(session, user, "inventory.view"):
        print("Access denied.")
        return

    print("\n===== LOW STOCK ALERTS =====")

    low_stock_parts = session.scalars(
        select(SparePart)
        .where(
            SparePart.stock_quantity <= SparePart.minimum_stock
        )
        .order_by(SparePart.stock_quantity)
    ).all()

    if not low_stock_parts:
        print("All spare parts are above minimum stock.")
        return

    for part in low_stock_parts:
        print("-" * 45)
        print(f"Part ID: {part.part_id}")
        print(f"Name: {part.part_name}")
        print(f"Stock: {part.stock_quantity}")
        print(f"Minimum Required: {part.minimum_stock}")

    print("-" * 45)
    print(f"Parts requiring attention: {len(low_stock_parts)}")
