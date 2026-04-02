import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_root_redirects_to_static_index_html():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "Science Club" in response.json()


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Science Club"
    email = "test.student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test.student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_student():
    # Arrange
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "unknown.student@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"


def test_remove_participant_from_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test.student@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
