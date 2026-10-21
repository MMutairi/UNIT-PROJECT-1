from sqlalchemy import ForeignKey, String
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