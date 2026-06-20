from datetime import datetime, timezone
from types import SimpleNamespace

from app.db import SessionLocal
from app.models import Booking, BookingStatus
from app.tasks import process_booking, send_mock_notification


def create_booking():
    with SessionLocal() as session:
        booking = Booking(
            name="Alice",
            datetime=datetime(2026, 6, 21, 10, tzinfo=timezone.utc),
            service_type="consultation",
            status=BookingStatus.pending,
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking.id


def get_status(booking_id):
    with SessionLocal() as session:
        return session.get(Booking, booking_id).status


def test_worker_confirms_booking_once(monkeypatch):
    booking_id = create_booking()
    sent = []

    monkeypatch.setattr("app.tasks.random.random", lambda: 0.2)
    monkeypatch.setattr("app.tasks.send_mock_notification", lambda booking: sent.append(booking.id))

    assert process_booking.run(booking_id) == "confirmed"
    assert process_booking.run(booking_id) is None
    assert get_status(booking_id) == BookingStatus.confirmed
    assert sent == [booking_id]


def test_worker_marks_failed_without_notification(monkeypatch):
    booking_id = create_booking()
    sent = []

    monkeypatch.setattr("app.tasks.random.random", lambda: 0.1)
    monkeypatch.setattr("app.tasks.send_mock_notification", lambda booking: sent.append(booking.id))

    assert process_booking.run(booking_id) == "failed"
    assert get_status(booking_id) == BookingStatus.failed
    assert sent == []


def test_mock_notification_logs_without_reserved_fields(caplog):
    booking = SimpleNamespace(id=1, name="Alice", service_type="consultation")

    caplog.set_level("INFO", logger="app.tasks")
    send_mock_notification(booking)

    assert "mock_notification_sent" in caplog.text
