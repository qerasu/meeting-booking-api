import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app, process_booking

if str(engine.url) != "sqlite://":
    raise RuntimeError("tests require sqlite://")


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(process_booking, "delay", lambda booking_id: None)
    with TestClient(app) as test_client:
        yield test_client
