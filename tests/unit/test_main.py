from re import fullmatch as regex_fullmatch

import pytest
from fastapi.testclient import TestClient

from app.main import app

TARGET_RECEIPT_JSON = {
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
        {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
        {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
        {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
        {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
        {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"},
    ],
    "total": "35.35",
}

# Initialize the TestClient
client = TestClient(app)


def test_ping_endpoint():
    """Test the /ping endpoint returns the expected response."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {
        "message": "pong"
    }, "Expected response body to be {'message': 'pong'}"


def test_ping_invalid_method():
    """Test the /ping endpoint with an invalid HTTP method."""
    response = client.post("/ping")
    assert response.status_code == 405


def test_receipts_process_target_example_returns_id():
    """Test the /receipts/process with receipt from github example for target"""
    request_body = TARGET_RECEIPT_JSON

    response = client.post("/receipts/process", json=request_body)

    # Request succeeded
    assert response.status_code == 200

    # Assert JSON format that contains only ID
    response_data = response.json()
    print(response_data)
    assert len(response_data) == 1, "The response should only have one entry - the id"
    assert "id" in response_data, "id was not in the response"

    # Assert format of id
    pattern = r"^\S+$"
    id = response_data["id"]
    assert regex_fullmatch(
        pattern=pattern, string=id
    ), f"{id} does not match expected regular expression pattern {pattern}"


def test_receipts_process_invalid_receipt_returns_400_bad_request():
    """Test the /receipts/process with malformed receipt that has no items"""
    request_body = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [],
        "total": "35.35",
    }

    response = client.post("/receipts/process", json=request_body)

    print(response.status_code)
    print(response.text)

    # BadRequest
    assert response.status_code == 400
    assert response.text == ""


def test_receipts_process_invalid_json_returns_400_bad_request():
    """Test the /receipts/process with malformed receipt that has no items"""
    request_body = "THIS IS NOT A JSON"

    response = client.post("/receipts/process", data=request_body)

    # BadRequest
    assert response.status_code == 400
    assert response.text == ""


def test_get_points_for_target_receipt_returns_correct_points():
    """Test the /receipts/process with malformed receipt that has no items"""

    # Arrange a valid receipt_id by calling process endpoint
    request_body = TARGET_RECEIPT_JSON
    process_response = client.post("/receipts/process", json=request_body)
    id = process_response.json()["id"]

    # Call the get points endpoint
    response = client.get(f"/receipts/{id}/points")

    # Request succeeded
    assert response.status_code == 200

    # Assert JSON format that contains only the points
    response_data = response.json()
    print(response_data)
    assert (
        len(response_data) == 1
    ), "The response should only have one entry - the points"
    assert "points" in response_data, "id was not in the response"
    assert response_data["points"] == 28


def test_get_points_for_non_existing_receipt():
    """Test get receipt points when no receipt id ever processed returns 404 not fuond"""
    id = "foo"

    # Call the get points endpoint
    response = client.get(f"/receipts/{id}/points")

    # No receipt should be found
    assert response.status_code == 404

    print(response.text)
    assert response.text == ""
