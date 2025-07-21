from jsonschema import validate as validate_schema
from jsonschema.exceptions import ValidationError
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id}
2) *Optional* Consider using @pytest.fixture to create unique test data for each run
2) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test
3) Validate the response codes and values
4) Validate the response message "Order and pet status updated successfully"
'''



@pytest.fixture
def new_order_payload():
    pet_reference_id = 2  # Assume this pet ID exists
    payload = {"pet_id": pet_reference_id}
    response = api_helpers.post_api_data("/store/order", payload)

    print("[DEBUG] Order Creation Response:", response.text)
    assert response.status_code == 201, "Expected 201 Created for order creation"
    
    return response.json()


def test_update_order_with_patch(new_order_payload):
    updated_order_data = {"pet_id": 1}  # Changing the pet ID

    order_id = new_order_payload.get("id")
    assert order_id is not None, "Order ID should not be None"

    patch_endpoint = f"/store/order/{order_id}"
    response = api_helpers.patch_api_data(patch_endpoint, updated_order_data)

    print("[DEBUG] Patch Response:", response.text)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    response_json = response.json()

    # Schema validation
    try:
        validate_schema(instance=response_json.get("order"), schema=schemas.order_schema)
        validate_schema(instance=response_json.get("pet"), schema=schemas.pet_schema)
    except ValidationError as ve:
        raise AssertionError(f"Schema validation failed: {ve}")

    # Message validation
    expected_message = "Order and pet status updated successfully"
    actual_message = response_json.get("message")
    assert_that(actual_message, is_(expected_message))

    # Field assertions
    assert_that(response_json["order"]["pet_id"], is_(1))
    assert_that(response_json["pet"]["status"], is_("sold"))

def test_patch_order_with_invalid_pet_id():
    invalid_order_id = "fake_pet"
    invalid_data = {"pet_id": 999}

    patch_url = f"/store/order/{invalid_order_id}"
    response = api_helpers.patch_api_data(patch_url, invalid_data)

    print("[DEBUG] Invalid Patch Response:", response.text)

    # Depending on API implementation: could return 400 or 404
    assert response.status_code in [400, 404], f"Unexpected status code: {response.status_code}"
    assert_that(response.text.lower(), contains_string("not found"))
