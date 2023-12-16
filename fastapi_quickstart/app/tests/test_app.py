from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_calculate_sum():
    response = client.get("/sum/?a=5&b=10")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"result": 15}

    # Test case 2: отрицательные числа
    response = client.get("/sum/?a=-8&b=-3")
    assert response.status_code == 200
    assert response.json() == {"result": -11}

    # Test case 3: ноль и положительное число
    response = client.get("/sum/?a=0&b=7")
    assert response.status_code == 200
    assert response.json() == {"result": 7}

    # Test case 4: одно число не введено
    response = client.get("/sum/?a=3")
    assert response.status_code == 422  # Unprocessable Entity (validation error)
