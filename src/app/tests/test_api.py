import httpx
import traceback
from app.models.schemas import Property, RentalUnits, RentalUnitsCalendarItem, RentalUnitsCalendar
from pydantic import ValidationError
from app.tests.constants import API_BASE_URL, HEADERS

def test_get_elements():
    response = httpx.get(f"{API_BASE_URL}/elements", headers=HEADERS)
    data = response.json()
    element_data = data.get("data", {})
    list_key_element = [
        "contractsModels",
        "features",
        "kitchen",
        "languages",
        "propertiesTypes",
        "rentalConditions",
        "rentalUnitsStates",
        "services",
    ]
   
    for key in list_key_element:
        assert key in element_data, f"Missing expected key: {key}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

def test_get_properties():
    response = httpx.get(f"{API_BASE_URL}/properties?limit=1", headers=HEADERS)
    data = response.json()
    print("API Response:", data)

    try:
        api_data = data.get("data", {}).get("rows", {})
        if api_data:
            result = Property(**api_data[0])
            print("result: ", result)
            assert response.status_code == 200
        else:
            print("No properties found")
            assert False

    except ValidationError as e:
        print("\n🚨 Validation Error Details:")
        for error in e.errors():
            print(
                f"❌ Campo: {error['loc']} | ❗ Error: {error['msg']} | 📌 Tipo: {error['type']}"
            )
        raise e  # Relanza la excepción para que pytest la capture

    except Exception as e:
        print("\n❌ Unexpected Exception:", e)
        print("🔍 Tipo de error:", type(e).__name__)
        traceback.print_exc()
        raise e


def test_get_rental_units():
    response = httpx.get(f"{API_BASE_URL}/rental-units?limit=1", headers=HEADERS)
    data = response.json()
    print("API Response:", data)

    try:
        api_data = data.get("data", {}).get("rows", {})
        if api_data:
            # Obtener rental_unit_id desde la primera propiedad de la respuesta
            rental_unit_id = api_data[0].get("id")
            result = RentalUnits(**api_data[0])  # Validación automática por Pydantic
            print("result: ", result)
            assert response.status_code == 200

            # Llamar al test para obtener el calendario, pasándole el rental_unit_id
            get_rental_unit_calendar(rental_unit_id)

        else:
            print("No rental units found")
            assert False  # Asegurar que haya rental units en la respuesta

    except ValidationError as e:
        print("\n🚨 Validation Error Details:")
        for error in e.errors():
            print(
                f"❌ Campo: {error['loc']} | ❗ Error: {error['msg']} | 📌 Tipo: {error['type']}"
            )
        raise e  # Relanzar la excepción para que pytest la capture

    except Exception as e:
        print("\n❌ Unexpected Exception:", e)
        print("🔍 Tipo de error:", type(e).__name__)
        traceback.print_exc()
        raise e


def get_rental_unit_calendar(rental_unit_id):
    response = httpx.get(f"{API_BASE_URL}/rental-units/{rental_unit_id}/calendar", headers=HEADERS)
    data = response.json()
    print("API Response:", data)

    try:
        api_data = data.get("data", {})
        if api_data:
            result = RentalUnitsCalendar(dates=api_data)
            print("result: ", result)
            assert response.status_code == 200
        else:
            print("No rental units found")
            assert False

    except ValidationError as e:
        print("\n🚨 Validation Error Details:")
        for error in e.errors():
            print(
                f"❌ Campo: {error['loc']} | ❗ Error: {error['msg']} | 📌 Tipo: {error['type']}"
            )
        raise e  # Relanza la excepción para que pytest la capture

    except Exception as e:
        print("\n❌ Unexpected Exception:", e)
        print("🔍 Tipo de error:", type(e).__name__)
        traceback.print_exc()
        raise e