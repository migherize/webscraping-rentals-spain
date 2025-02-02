import httpx
import traceback
from app.models.schemas import Property
from pydantic import ValidationError
from app.tests.constants import API_BASE_URL, HEADERS

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
            print(f"❌ Campo: {error['loc']} | ❗ Error: {error['msg']} | 📌 Tipo: {error['type']}")
        raise e  # Relanza la excepción para que pytest la capture

    except Exception as e:
        print("\n❌ Unexpected Exception:", e)
        print("🔍 Tipo de error:", type(e).__name__)
        traceback.print_exc()
        raise e


def test_get_elements():
    response = httpx.get(f"{API_BASE_URL}/elements", headers=HEADERS)
    data = response.json()
    print("data: ", data)
    assert response.status_code == 200
