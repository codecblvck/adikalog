from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    pin_hash: Mapped[str] = mapped_column(String(256))
    failed_attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    @property
    def pin(self):
        raise AttributeError("pin is write-only")

    @pin.setter
    def pin(self, value):
        self.pin_hash = generate_password_hash(value)

    def check_pin(self, plain_pin):
        return check_password_hash(self.pin_hash, plain_pin)

    def __repr__(self) -> str:
        return f"User(name={self.name})"


class Sale(db.Model):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_key: Mapped[str] = mapped_column(String(64), unique=True)
    customer_name: Mapped[str | None] = mapped_column(String(64))
    discount: Mapped[int] = mapped_column(default=0, server_default="0")
    total: Mapped[int] = mapped_column()
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale", order_by="SaleItem.id"
    )

    __table_args__ = (
        CheckConstraint("discount >= 0", name="ck_sales_discount_min"),
        CheckConstraint("total > 0", name="ck_sales_total_positive"),
    )

    @property
    def receipt_no(self) -> str:
        return f"{self.id:04d}"


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    product_name: Mapped[str] = mapped_column(String(120))
    quantity: Mapped[int] = mapped_column()
    selling_price: Mapped[int] = mapped_column()

    sale: Mapped["Sale"] = relationship(back_populates="items")

    __table_args__ = (
        CheckConstraint("quantity >= 1", name="ck_sale_items_quantity_min"),
        CheckConstraint("selling_price >= 1", name="ck_sale_items_selling_price_min"),
    )
