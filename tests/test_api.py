from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity data before and after each test."""
    original = deepcopy(activities)
    activities.clear()
    activities.update(deepcopy(original))

    yield

    activities.clear()
    activities.update(deepcopy(original))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "participants" in payload[expected_activity]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_registration(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Unknown Activity/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_for_non_member_returns_400(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
