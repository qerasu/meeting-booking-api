import logging
import os
import random

from celery import Celery
from sqlalchemy import update

from .db import SessionLocal
from .models import Booking, BookingStatus

celery_app = Celery(
    "bookings",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)
logger = logging.getLogger(__name__)


def send_mock_notification(booking):
    logger.info(
        "mock_notification_sent",
        extra={
            "booking_id": booking.id,
            "booking_name": booking.name,
            "service_type": booking.service_type,
        },
    )


@celery_app.task(name="app.tasks.process_booking")
def process_booking(booking_id):
    target_status = (
        BookingStatus.failed
        if random.random() < 0.15
        else BookingStatus.confirmed
    )

    with SessionLocal() as session:
        result = session.execute(
            update(Booking)
            .where(
                Booking.id == booking_id,
                Booking.status == BookingStatus.pending,
            )
            .values(status=target_status)
        )
        session.commit()

        if result.rowcount != 1:
            return None

        if target_status == BookingStatus.confirmed:
            booking = session.get(Booking, booking_id)
            send_mock_notification(booking)

        return target_status.value
