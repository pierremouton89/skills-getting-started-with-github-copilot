import pytest
from fastapi.testclient import TestClient
from src.app import app  # Import the FastAPI app

client = TestClient(app)


def test_root_redirect():
    # Arrange: No special setup needed

    # Act: Make GET request to root
    response = client.get("/")

    # Assert: Should serve the index.html (redirect followed or direct serve)
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Mergington High School" in response.text


def test_get_activities():
    # Arrange: No special setup needed

    # Act: Make GET request to activities
    response = client.get("/activities")

    # Assert: Should return 200 and contain expected activities
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert "description" in data["Chess Club"]


def test_signup_success():
    # Arrange: Use a unique email not in initial data
    email = "newstudent@test.edu"
    activity = "Chess Club"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Should return 200 and success message, and email added to participants
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]

    # Verify in data
    get_response = client.get("/activities")
    assert email in get_response.json()[activity]["participants"]


def test_signup_activity_not_found():
    # Arrange: Use non-existent activity
    email = "test@test.com"
    activity = "Nonexistent Activity"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Should return 404 with error message
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_signup_already_signed_up():
    # Arrange: Sign up first, then try again
    email = "duplicate@test.com"
    activity = "Programming Class"

    # First signup
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Try to signup again
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Should return 400 with error message
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_unregister_success():
    # Arrange: Sign up first, then unregister
    email = "unreg@test.com"
    activity = "Gym Class"

    # Signup
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Should return 200 and success message, and email removed from participants
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]

    # Verify removed
    get_response = client.get("/activities")
    assert email not in get_response.json()[activity]["participants"]


def test_unregister_activity_not_found():
    # Arrange: Use non-existent activity
    email = "test@test.com"
    activity = "Nonexistent Activity"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Should return 404 with error message
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_not_signed_up():
    # Arrange: Try to unregister without signing up
    email = "notsigned@test.com"
    activity = "Basketball Team"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Should return 400 with error message
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]