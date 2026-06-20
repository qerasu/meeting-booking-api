from datetime import datetime as dt

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_session
from .models import Booking, BookingStatus
from .tasks import process_booking

app = FastAPI(title="Bookings API")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "docs": "/docs", "bookings": "/bookings"}


class BookingCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    datetime: dt
    service_type: str = Field(min_length=1, max_length=100)


class BookingRead(BaseModel):
    id: int
    name: str
    datetime: dt
    service_type: str
    status: BookingStatus
    created_at: dt
    updated_at: dt

    model_config = ConfigDict(from_attributes=True)


@app.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate, session: Session = Depends(get_session)):
    booking = Booking(**payload.model_dump(), status=BookingStatus.pending)

    session.add(booking)
    session.commit()
    session.refresh(booking)
    process_booking.delay(booking.id)

    return booking


@app.get("/bookings/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking not found")

    return booking


@app.get("/bookings", response_model=list[BookingRead])
def list_bookings(
    status_filter: BookingStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    query = select(Booking).order_by(Booking.created_at.desc(), Booking.id.desc())

    if status_filter is not None:
        query = query.where(Booking.status == status_filter)

    return session.scalars(query.offset(offset).limit(limit)).all()


@app.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking not found")

    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="only pending bookings can be deleted")

    session.delete(booking)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
