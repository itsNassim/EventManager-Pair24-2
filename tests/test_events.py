import pytest
from pydantic import ValidationError

from app.schemas import EventCreate
from app.services.search import filter_events_by_location, filter_events_by_title


# --- Happy path (2) ---

def test_valid_event_created(sample_event_dict):
    event = EventCreate(**sample_event_dict)
    assert event.title == "Python Meetup"
    assert event.capacity == 50


def test_filter_by_location_returns_matches(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "constantine")
    assert len(result) == 2


# --- Boundary values (3) ---

def test_title_length_exactly_three_is_valid():
    event = EventCreate(title="AI!", location="Oran", date="2030-01-01", capacity=10)
    assert event.title == "AI!"


def test_capacity_minimum_boundary_is_valid():
    event = EventCreate(title="Demo", location="Oran", date="2030-01-01", capacity=1)
    assert event.capacity == 1


def test_capacity_maximum_boundary_is_valid():
    event = EventCreate(title="Demo", location="Oran", date="2030-01-01", capacity=10000)
    assert event.capacity == 10000


# --- Negative tests (2+) ---

def test_short_title_raises_validation_error():
    with pytest.raises(ValidationError):
        EventCreate(title="AI", location="Oran", date="2030-01-01", capacity=10)


@pytest.mark.parametrize("bad_capacity", [0, -5, 10001])
def test_invalid_capacity_raises_validation_error(bad_capacity):
    with pytest.raises(ValidationError):
        EventCreate(title="Demo", location="Oran", date="2030-01-01", capacity=bad_capacity)


# --- Case-insensitive title filter ---

def test_filter_by_title_is_case_insensitive(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "PYTHON")
    assert len(result) == 2