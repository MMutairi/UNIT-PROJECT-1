
"""Core Reception functions for AutoCare."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.auth.permissions import has_permission
from app.database.workshop_models import Customer, Vehicle


def register_customer(session, user):
    """Register a new customer."""

    if not has_permission(session, user, "customers.create"):
        print("Access denied.")
        return

    print("\n===== REGISTER CUSTOMER =====")

    name = input("Full name: ").strip()
    phone = input("Phone number: ").strip()

    if not name or len(name) > 30:
        print("Name must contain 1 to 30 characters.")
        return

    if not (phone.isascii() and phone.isdigit() and len(phone) == 10):
        print("Phone must contain exactly 10 digits.")
        return

    customer = Customer(
        full_name=name,
        phone=phone
    )

    try:
        session.add(customer)
        session.commit()
        print(f"Customer registered! ID: {customer.customer_id}")
    except IntegrityError:
        session.rollback()
        print("Could not register customer.")


def register_vehicle(session, user):
    """Register a vehicle for an existing customer."""

    if not has_permission(session, user, "vehicles.create"):
        print("Access denied.")
        return

    print("\n===== REGISTER VEHICLE =====")

    customer_id = input("Customer ID: ").strip()

    if not customer_id.isascii() or not customer_id.isdigit():
        print("Invalid customer ID.")
        return

    customer = session.get(Customer, int(customer_id))

    if customer is None:
        print("Customer not found.")
        return

    vin = input("VIN (17 characters): ").strip().upper()
    plate = input("Plate number: ").strip().upper()
    manufacturer = input("Manufacturer: ").strip()
    model = input("Model: ").strip()

    if len(vin) != 17 or not vin.isascii() or not vin.isalnum():
        print("VIN must contain 17 letters/numbers.")
        return

    if not plate or len(plate) > 10:
        print("Plate number must contain 1 to 10 characters.")
        return

    if not manufacturer or len(manufacturer) > 15:
        print("Invalid manufacturer.")
        return

    if not model or len(model) > 15:
        print("Invalid vehicle model.")
        return

    try:
        year = int(input("Model year: "))
        mileage = int(input("Mileage: "))
    except ValueError:
        print("Year and mileage must be numbers.")
        return

    if year < 1886 or year > datetime.now().year + 1:
        print("Invalid model year.")
        return

    if mileage < 0:
        print("Mileage cannot be negative.")
        return

    vehicle = Vehicle(
        customer_id=customer.customer_id,
        vin_number=vin,
        plate_number=plate,
        manufacturer=manufacturer,
        model=model,
        model_year=year,
        mileage=mileage
    )

    try:
        session.add(vehicle)
        session.commit()
        print(f"Vehicle registered! ID: {vehicle.vehicle_id}")
    except IntegrityError:
        session.rollback()
        print("Vehicle registration failed. Check VIN and plate uniqueness.")


def search_customer(session, user):
    """Search for a customer using their ID."""

    if not has_permission(session, user, "customers.view"):
        print("Access denied.")
        return

    print("\n===== SEARCH CUSTOMER =====")

    customer_id = input("Customer ID: ").strip()

    if not customer_id.isascii() or not customer_id.isdigit():
        print("Invalid customer ID.")
        return

    customer = session.get(Customer, int(customer_id))

    if customer is None:
        print("Customer not found.")
        return

    print(f"\nCustomer ID: {customer.customer_id}")
    print(f"Name: {customer.full_name}")
    print(f"Phone: {customer.phone}")


def view_customer_vehicles(session, user):
    """Display vehicles belonging to a customer."""

    if not has_permission(session, user, "vehicles.view"):
        print("Access denied.")
        return

    print("\n===== CUSTOMER VEHICLES =====")

    customer_id = input("Customer ID: ").strip()

    if not customer_id.isascii() or not customer_id.isdigit():
        print("Invalid customer ID.")
        return

    customer = session.get(Customer, int(customer_id))

    if customer is None:
        print("Customer not found.")
        return

    vehicles = session.scalars(
        select(Vehicle).where(
            Vehicle.customer_id == customer.customer_id
        )
    ).all()

    print(f"\nCustomer: {customer.full_name}")

    if not vehicles:
        print("No registered vehicles.")
        return

    for vehicle in vehicles:
        print(
            f"ID: {vehicle.vehicle_id} | "
            f"{vehicle.manufacturer} {vehicle.model} | "
            f"Year: {vehicle.model_year} | "
            f"Plate: {vehicle.plate_number}"
        )
