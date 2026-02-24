import pytest


def test_root_redirect(client):
    # Arrange: No special setup needed

    # Act: Make GET request to root
    response = client.get("/")

    # Assert: Check that it serves the static HTML file (redirect followed by TestClient)
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Mergington High School" in response.text


def test_get_activities(client):
    # Arrange: No special setup needed

    # Act: Make GET request to activities
    response = client.get("/activities")

    # Assert: Check success and data structure
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert "description" in data["Chess Club"]


def test_signup_success(client):
    # Arrange: Prepare email and activity
    email = "new@student.edu"
    activity = "Chess Club"

    # Act: Make POST request to signup with email as query param
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check success and participant added
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]


def test_signup_activity_not_found(client):
    # Arrange: Use non-existent activity
    email = "test@test.com"

    # Act: Make POST request with email as query param
    response = client.post("/activities/Nonexistent/signup", params={"email": email})

    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_signed_up(client):
    # Arrange: Sign up first
    email = "duplicate@test.com"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check 400 error
    assert response.status_code == 400
    assert "Student already signed up" in response.json()["detail"]


def test_remove_participant_success(client):
    # Arrange: Add participant first
    email = "remove@test.com"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert: Check success and participant removed
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_remove_participant_not_found(client):
    # Arrange: Use non-existent participant

    # Act: Make DELETE request
    response = client.delete("/activities/Chess Club/participants/nonexistent@test.com")

    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_remove_activity_not_found(client):
    # Arrange: Use non-existent activity

    # Act: Make DELETE request
    response = client.delete("/activities/Nonexistent/participants/test@test.com")

    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]