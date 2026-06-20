from app.db import SessionLocal
from app.models import Booking, BookingStatus


def booking_payload(name="Alice"):
    return {
        "name": name,
        "datetime": "2026-06-21T10:00:00+00:00",
        "service_type": "consultation",
    }


def set_status(booking_id, status):
    with SessionLocal() as session:
        booking = session.get(Booking, booking_id)
        booking.status = status
        session.commit()


def test_create_and_get_booking(client):
    created = client.post("/bookings", json=booking_payload())

    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "pending"
    assert body["name"] == "Alice"

    fetched = client.get(f"/bookings/{body['id']}")

    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


def test_list_bookings_filters_and_paginates(client):
    first = client.post("/bookings", json=booking_payload("Alice")).json()
    second = client.post("/bookings", json=booking_payload("Bob")).json()
    set_status(first["id"], BookingStatus.confirmed)

    response = client.get("/bookings", params={"status": "pending", "limit": 1, "offset": 0})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [second["id"]]


def test_delete_pending_booking(client):
    booking = client.post("/bookings", json=booking_payload()).json()

    deleted = client.delete(f"/bookings/{booking['id']}")

    assert deleted.status_code == 204
    assert client.get(f"/bookings/{booking['id']}").status_code == 404


def test_delete_confirmed_booking_is_rejected(client):
    booking = client.post("/bookings", json=booking_payload()).json()
    set_status(booking["id"], BookingStatus.confirmed)

    response = client.delete(f"/bookings/{booking['id']}")

    assert response.status_code == 409


def test_create_booking_validates_payload(client):
    response = client.post("/bookings", json={**booking_payload(), "name": ""})

    assert response.status_code == 422
