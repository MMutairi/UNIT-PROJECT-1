from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Boolean, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(primary_key=True)

    full_name: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str] = mapped_column(String(10))

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="customer"
    )
class Vehicle(Base):
    __tablename__ = "vehicles"
    vehicle_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False
    )
    vin_number: Mapped[str] = mapped_column(
        String(17),
        unique=True,
        nullable=False
    )
    plate_number: Mapped[str] = mapped_column(
        String(10),
        unique=True
    )
    manufacturer: Mapped[str] = mapped_column(String(15))
    model: Mapped[str] = mapped_column(String(15))
    model_year: Mapped[int]
    mileage: Mapped[int] = mapped_column(default=0)
    customer: Mapped["Customer"] = relationship(
        back_populates="vehicles"
    )
    repair_tickets: Mapped[list["RepairTicket"]] = relationship(
    back_populates="vehicle"
    )
class Mechanic(Base):
    __tablename__ = "mechanics"
    mechanic_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    specialty: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    repair_tickets: Mapped[list["RepairTicket"]] = relationship(
        back_populates="mechanic"
    )
class RepairTicket(Base):
    __tablename__ = "repair_tickets"
    ticket_id: Mapped[int] = mapped_column(
        primary_key=True
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.vehicle_id"),
        nullable=False
    )
    mechanic_id: Mapped[int | None] = mapped_column(
        ForeignKey("mechanics.mechanic_id"),
        nullable=True
    )
    problem_description: Mapped[str] = mapped_column(
        String(255)
    )
    diagnosis: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="Pending"
    )
    vehicle: Mapped["Vehicle"] = relationship(
        back_populates="repair_tickets"
    )
    mechanic: Mapped["Mechanic | None"] = relationship(
        back_populates="repair_tickets"
    )
    parts_used: Mapped[list["RepairPart"]] = relationship(
        back_populates="repair_ticket"
    )
    invoice: Mapped["Invoice | None"] = relationship(
    back_populates="repair_ticket",
    uselist=False
    )
class SparePart(Base):
    __tablename__ = "spare_parts"
    part_id: Mapped[int] = mapped_column(primary_key=True)
    part_name: Mapped[str] = mapped_column(String(100))
    part_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    stock_quantity: Mapped[int] = mapped_column(default=0)
    
    minimum_stock: Mapped[int] = mapped_column(default=5)
    
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    repair_parts: Mapped[list["RepairPart"]] = relationship(
        back_populates="spare_part"
    )
class RepairPart(Base):
    __tablename__ = "repair_parts"
    repair_part_id: Mapped[int] = mapped_column(
        primary_key=True
    )
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("repair_tickets.ticket_id"),
        nullable=False
    )
    part_id: Mapped[int] = mapped_column(
        ForeignKey("spare_parts.part_id"),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    repair_ticket: Mapped["RepairTicket"] = relationship(
        back_populates="parts_used"
    )
    spare_part: Mapped["SparePart"] = relationship(
        back_populates="repair_parts"
    )
class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("repair_tickets.ticket_id"),
        unique=True,
        nullable=False
    )

    parts_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00")
    )

    labor_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00")
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00")
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Unpaid"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    repair_ticket: Mapped["RepairTicket"] = relationship(
        back_populates="invoice"
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="invoice"
    )
class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.invoice_id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    payment_method: Mapped[str] = mapped_column(
        String(30)
    )

    paid_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="payments"
    )
