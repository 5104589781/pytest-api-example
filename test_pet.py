from jsonschema import validate as validate_schema, ValidationError
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_


def test_validate_pet_schema_response():
    endpoint = "/pets/"
    response = api_helpers.get_api_data(endpoint)

    # Check status code
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"

    # Output response for debugging
    print("API Response:", response.json())

    # Schema validation
    try:
        validate_schema(instance=response.json(), schema=schemas.pet_schema)
        print(" Response matches the expected schema.")
    except ValidationError as validation_error:
        print(" Schema validation failed:", validation_error)
        raise


@pytest.mark.parametrize("expected_status", ["available", "pending", "sold"])
def test_find_pets_by_status(expected_status):
    endpoint = "/pets/findByStatus"
    params = {"status": expected_status}

    response = api_helpers.get_api_data(endpoint, params=params)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    pets_list = response.json()

    for idx, pet in enumerate(pets_list):
        assert pet.get("status") == expected_status, (
            f"Pet at index {idx} has unexpected status. Expected: '{expected_status}', Got: '{pet.get('status')}'"
        )
        assert "id" in pet and isinstance(pet["id"], int), f"Missing or invalid 'id' at index {idx}"
        assert "name" in pet and isinstance(pet["name"], str), f"Missing or invalid 'name' at index {idx}"
        assert "type" in pet and pet["type"] in ["cat", "dog", "fish"], f"Invalid 'type' at index {idx}"
        assert "status" in pet and pet["status"] in ["available", "pending", "sold"], f"Invalid 'status' at index {idx}"

        try:
            validate_schema(instance=pet, schema=schemas.pet_schema)
        except ValidationError as e:
            raise AssertionError(f"Schema validation failed for pet at index {idx}: {e}")

def test_invalid_pet_id_returns_404(invalid_pet_id):
    endpoint = f"/pets/{invalid_pet_id}"

    response = api_helpers.get_api_data(endpoint)

    assert response.status_code == 404, (
        f"Expected 404 Not Found, but received {response.status_code} for pet_id: {invalid_pet_id}"
    )
