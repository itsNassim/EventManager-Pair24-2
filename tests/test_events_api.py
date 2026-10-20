import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Separate in-memory database for tests, so events.db is never touched
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as c:
        yield c


EVENT = {
    "title": "Python Meetup",
    "description": "Intro talk",
    "date": "2030-01-15",
    "location": "Constantine",
    "capacity": 50,
}


def test_create_event_returns_201(client):
    response = client.post("/events/", json=EVENT)
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_create_event_in_past_returns_400(client):
    response = client.post("/events/", json={**EVENT, "date": "2000-01-01"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Event date cannot be in the past."


def test_create_event_with_short_title_returns_422(client):
    response = client.post("/events/", json={**EVENT, "title": "AI"})
    assert response.status_code == 422


def test_get_event_returns_200(client):
    created = client.post("/events/", json=EVENT).json()
    response = client.get(f"/events/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Python Meetup"


def test_get_missing_event_returns_404(client):
    response = client.get("/events/999")
    assert response.status_code == 404


def test_list_events_filters_by_location(client):
    client.post("/events/", json=EVENT)
    client.post("/events/", json={**EVENT, "title": "Cyber Summit", "location": "Algiers"})
    response = client.get("/events/", params={"location": "constantine"})
    assert len(response.json()) == 1


def test_list_events_filters_by_title(client):
    client.post("/events/", json=EVENT)
    client.post("/events/", json={**EVENT, "title": "Cyber Summit"})
    response = client.get("/events/", params={"title": "python"})
    assert len(response.json()) == 1


def test_update_event_returns_200(client):
    created = client.post("/events/", json=EVENT).json()
    response = client.put(f"/events/{created['id']}", json={**EVENT, "capacity": 80})
    assert response.status_code == 200
    assert response.json()["capacity"] == 80


def test_delete_event_then_get_returns_404(client):
    created = client.post("/events/", json=EVENT).json()
    assert client.delete(f"/events/{created['id']}").status_code == 204
    assert client.get(f"/events/{created['id']}").status_code == 404