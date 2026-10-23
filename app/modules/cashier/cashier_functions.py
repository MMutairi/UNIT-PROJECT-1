
"""Core Cashier functions for AutoCare."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.auth.permissions import has_permission
from app.database.workshop_models import (
    Invoice,
    Payment,
    RepairPart,
    RepairTicket,
)


VAT_RATE = Decimal("0.15")
CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("99999999.99")

PAYMENT_METHODS = {
    "1": "Cash",
    "2": "Card",
    "3": "Bank Transfer",
}


def read_money(prompt, allow_zero=False):
    """Read a valid monetary amount using Decimal."""

    raw = input(prompt).strip()

    try:
        amount = Decimal(raw)

        if not amount.is_finite():
            raise ValueError

        if amount < 0 or (amount == 0 and not allow_zero):
            raise ValueError

        if amount > MAX_AMOUNT:
            raise ValueError

        if amount != amount.quantize(CENT):
            raise ValueError

        return amount

    except (InvalidOperation, ValueError):
        print("Invalid amount. Use a positive value with up to 2 decimals.")
        return None


def read_positive_id(prompt):
    """Read a positive database ID."""

    value = input(prompt).strip()

    if not value.isascii() or not value.isdigit():
        print("Please enter a valid ID.")
        return None

    number = int(value)

    if number <= 0:
        print("ID must be greater than zero.")
        return None

    return number


def get_total_paid(session, invoice_id):
    """Calculate total payments recorded for an invoice."""

    amounts = session.scalars(
        select(Payment.amount).where(
            Payment.invoice_id == invoice_id
        )
    ).all()

    return sum(amounts, Decimal("0.00"))


def create_invoice(session, user):
    """Create an invoice for a completed repair ticket."""

    if not has_permission(session, user, "invoices.create"):
        print("Access denied.")
        return

    print("\n========== CREATE INVOICE ==========")

    ticket_id = read_positive_id("Repair Ticket ID: ")

    if ticket_id is None:
        return

    ticket = session.get(RepairTicket, ticket_id)

    if ticket is None:
        print("Repair ticket not found.")
        return

    if ticket.status != "Completed":
        print("The repair must be completed before invoicing.")
        return

    existing_invoice = session.scalar(
        select(Invoice).where(
            Invoice.ticket_id == ticket_id
        )
    )

    if existing_invoice is not None:
        print(
            f"This ticket already has invoice "
            f"#{existing_invoice.invoice_id}."
        )
        return

    repair_parts = session.scalars(
        select(RepairPart).where(
            RepairPart.ticket_id == ticket_id
        )
    ).all()

    parts_total = sum(
        (
            part.unit_price * part.quantity
            for part in repair_parts
        ),
        Decimal("0.00"),
    ).quantize(CENT)

    print(f"\nRepair Ticket: {ticket.ticket_id}")
    print(f"Parts Total: {parts_total:.2f} SAR")

    labor_cost = read_money(
        "Labor Cost (SAR): ",
        allow_zero=True
    )

    if labor_cost is None:
        return

    subtotal = parts_total + labor_cost

    if subtotal <= 0:
        print("An invoice must have a positive total.")
        return

    tax_amount = (
        subtotal * VAT_RATE
    ).quantize(CENT, rounding=ROUND_HALF_UP)

    total_amount = subtotal + tax_amount

    if (
        parts_total > MAX_AMOUNT
        or subtotal > MAX_AMOUNT
        or total_amount > MAX_AMOUNT
    ):
        print("Invoice amount exceeds the supported limit.")
        return

    print("\n========== INVOICE SUMMARY ==========")
    print(f"Parts:    {parts_total:.2f} SAR")
    print(f"Labor:    {labor_cost:.2f} SAR")
    print(f"Subtotal: {subtotal:.2f} SAR")
    print(f"VAT 15%:  {tax_amount:.2f} SAR")
    print("-" * 35)
    print(f"TOTAL:    {total_amount:.2f} SAR")

    confirm = input(
        "\nCreate this invoice? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Invoice creation cancelled.")
        return

    invoice = Invoice(
        ticket_id=ticket.ticket_id,
        parts_total=parts_total,
        labor_cost=labor_cost,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status="Unpaid",
    )

    try:
        session.add(invoice)
        session.commit()

        print("\nInvoice created successfully!")
        print(f"Invoice ID: {invoice.invoice_id}")
        print(f"Amount Due: {invoice.total_amount:.2f} SAR")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to create invoice.")


def view_invoice(session, user):
    """Display an invoice and its remaining balance."""

    if not has_permission(session, user, "invoices.view"):
        print("Access denied.")
        return

    print("\n========== VIEW INVOICE ==========")

    invoice_id = read_positive_id("Invoice ID: ")

    if invoice_id is None:
        return

    invoice = session.get(Invoice, invoice_id)

    if invoice is None:
        print("Invoice not found.")
        return

    paid = get_total_paid(session, invoice.invoice_id)
    balance = invoice.total_amount - paid

    print("\n========== INVOICE DETAILS ==========")
    print(f"Invoice ID:   {invoice.invoice_id}")
    print(f"Ticket ID:    {invoice.ticket_id}")
    print(f"Created At:   {invoice.created_at}")
    print("-" * 40)
    print(f"Parts Total:  {invoice.parts_total:.2f} SAR")
    print(f"Labor Cost:   {invoice.labor_cost:.2f} SAR")
    print(f"VAT:          {invoice.tax_amount:.2f} SAR")
    print(f"Total:        {invoice.total_amount:.2f} SAR")
    print("-" * 40)
    print(f"Total Paid:   {paid:.2f} SAR")
    print(f"Balance Due:  {balance:.2f} SAR")
    print(f"Status:       {invoice.status}")


def record_payment(session, user):
    """Record a full or partial payment for an invoice."""

    if not has_permission(session, user, "payments.create"):
        print("Access denied.")
        return

    print("\n========== RECORD PAYMENT ==========")

    invoice_id = read_positive_id("Invoice ID: ")

    if invoice_id is None:
        return

    invoice = session.get(Invoice, invoice_id)

    if invoice is None:
        print("Invoice not found.")
        return

    paid = get_total_paid(session, invoice_id)
    balance = invoice.total_amount - paid

    if balance <= 0:
        print("This invoice has no outstanding balance.")
        return

    print(f"\nInvoice Total: {invoice.total_amount:.2f} SAR")
    print(f"Already Paid:  {paid:.2f} SAR")
    print(f"Balance Due:   {balance:.2f} SAR")

    amount = read_money("Payment Amount (SAR): ")

    if amount is None:
        return

    if amount > balance:
        print("Payment cannot exceed the remaining balance.")
        return

    print("\nPayment Methods:")

    for number, method in PAYMENT_METHODS.items():
        print(f"{number}. {method}")

    choice = input("Select payment method: ").strip()

    if choice not in PAYMENT_METHODS:
        print("Invalid payment method.")
        return

    payment_method = PAYMENT_METHODS[choice]

    new_total_paid = paid + amount
    new_balance = invoice.total_amount - new_total_paid

    print("\n========== PAYMENT SUMMARY ==========")
    print(f"Amount:  {amount:.2f} SAR")
    print(f"Method:  {payment_method}")
    print(f"Balance: {new_balance:.2f} SAR")

    confirm = input(
        "\nConfirm payment? (y/N): "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("Payment cancelled.")
        return

    try:
        payment = Payment(
            invoice_id=invoice.invoice_id,
            amount=amount,
            payment_method=payment_method,
        )

        session.add(payment)

        if new_balance == 0:
            invoice.status = "Paid"
        else:
            invoice.status = "Partially Paid"

        session.commit()

        print("\nPayment recorded successfully!")
        print(f"Payment ID: {payment.payment_id}")
        print(f"Invoice Status: {invoice.status}")
        print(f"Remaining Balance: {new_balance:.2f} SAR")

    except SQLAlchemyError:
        session.rollback()
        print("Failed to record payment.")


def view_unpaid_invoices(session, user):
    """Display invoices with outstanding balances."""

    if not has_permission(session, user, "invoices.view"):
        print("Access denied.")
        return

    print("\n========== OUTSTANDING INVOICES ==========")

    invoices = session.scalars(
        select(Invoice).order_by(Invoice.invoice_id)
    ).all()

    outstanding_count = 0
    total_outstanding = Decimal("0.00")

    for invoice in invoices:
        paid = get_total_paid(session, invoice.invoice_id)
        balance = invoice.total_amount - paid

        if balance <= 0:
            continue

        outstanding_count += 1
        total_outstanding += balance

        print("-" * 45)
        print(f"Invoice ID: {invoice.invoice_id}")
        print(f"Ticket ID: {invoice.ticket_id}")
        print(f"Total: {invoice.total_amount:.2f} SAR")
        print(f"Paid: {paid:.2f} SAR")
        print(f"Balance: {balance:.2f} SAR")
        print(f"Status: {invoice.status}")

    if outstanding_count == 0:
        print("No outstanding invoices.")
        return

    print("-" * 45)
    print(f"Outstanding Invoices: {outstanding_count}")
    print(f"Total Due: {total_outstanding:.2f} SAR")


def view_payment_history(session, user):
    """Display recorded customer payments."""

    if not has_permission(session, user, "payments.view"):
        print("Access denied.")
        return

    print("\n========== PAYMENT HISTORY ==========")

    payments = session.scalars(
        select(Payment).order_by(
            Payment.paid_at,
            Payment.payment_id,
        )
    ).all()

    if not payments:
        print("No payments recorded.")
        return

    total_received = Decimal("0.00")

    for payment in payments:
        total_received += payment.amount

        print("-" * 45)
        print(f"Payment ID: {payment.payment_id}")
        print(f"Invoice ID: {payment.invoice_id}")
        print(f"Amount: {payment.amount:.2f} SAR")
        print(f"Method: {payment.payment_method}")
        print(f"Date: {payment.paid_at}")

    print("-" * 45)
    print(f"Total Payments: {len(payments)}")
    print(f"Total Received: {total_received:.2f} SAR")
