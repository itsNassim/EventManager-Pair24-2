import pytest

from app.schemas import EventCreate


@pytest.fixture
def sample_event_dict():
    return {
        "title": "Python Meetup",
        "description": "Intro talk",
        "date": "2030-01-15",
        "location": "Constantine",
        "capacity": 50,
    }


@pytest.fixture
def sample_participant_dict():
    return {"name": "Nass", "email": "nass@example.com"}


@pytest.fixture
def mock_event_store():
    store = []          # in-memory repository, no database
    yield store
    store.clear()       # teardown


@pytest.fixture
def prepopulated_event_store(mock_event_store):
    mock_event_store.extend([
        EventCreate(title="Python Meetup", location="Constantine",
                    date="2030-01-15", capacity=50),
        EventCreate(title="Cyber Summit", location="Algiers",
                    date="2030-02-10", capacity=200),
        EventCreate(title="Python Workshop", location="Constantine",
                    date="2030-03-05", capacity=20),
    ])
    return mock_event_store


@pytest.fixture(autouse=True)
def global_environment_logger():
    print("\n[SETUP] test starting")
    yield
    print("\n[TEARDOWN] test finished")