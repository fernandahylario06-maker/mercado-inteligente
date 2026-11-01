from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def current_utc_time():
    return datetime.now()


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_product_name",
        ),
        CheckConstraint(
            "length(trim(category)) > 0",
            name="ck_product_category",
        ),
        CheckConstraint(
            "length(trim(unit)) > 0",
            name="ck_product_unit",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
    )
    category: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="unidade",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=current_utc_time,
        nullable=False,
    )

    batches: Mapped[list["Batch"]] = relationship(
        back_populates="product"
    )
    movements: Mapped[list["Movement"]] = relationship(
        back_populates="product"
    )


class Batch(Base):
    __tablename__ = "batches"

    __table_args__ = (
        CheckConstraint(
            "quantity >= 0",
            name="ck_batch_quantity",
        ),
        CheckConstraint(
            "length(trim(code)) > 0",
            name="ck_batch_code",
        ),
        CheckConstraint(
            "expires_at >= received_at",
            name="ck_batch_expiry",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    received_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    expires_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        back_populates="batches"
    )
    movements: Mapped[list["Movement"]] = relationship(
        back_populates="batch"
    )


class Movement(Base):
    __tablename__ = "movements"

    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('entrada', 'saida')",
            name="ck_movement_type",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_movement_quantity",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("batches.id"),
        nullable=False,
    )
    movement_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=current_utc_time,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    product: Mapped["Product"] = relationship(
        back_populates="movements"
    )
    batch: Mapped["Batch"] = relationship(
        back_populates="movements"
    )