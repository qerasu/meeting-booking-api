from datetime import datetime as dt, timezone
from enum import Enum

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    datetime: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(BookingStatus, name="booking_status", native_enum=False),
        nullable=False,
        default=BookingStatus.pending,
    )
    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.now(timezone.utc),
        onupdate=lambda: dt.now(timezone.utc),
        nullable=False,
    )
