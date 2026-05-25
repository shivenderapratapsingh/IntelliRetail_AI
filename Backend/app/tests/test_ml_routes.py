from fastapi.testclient import TestClient

from app.api.main import app


#intialize

client = TestClient(app)


#to test forecast api

def test_forecast_endpoint():

    payload = {

        "quantity": 10,

        "profit": 250,

        "returns": 1,

        "order_year": 2025,

        "order_month": 11,

        "order_day": 15,

        "profit_margin": 22,

        "shipping_days": 3
    }

    response = client.post(

        "/ml-expert/forecast",

        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] == True

    assert "prediction" in data

#test anomaly api

def test_anomaly_endpoint():

    payload = {

        "sales": 10000,

        "profit": -5000,

        "quantity": 1,

        "profit_margin": -50,

        "shipping_days": 15
    }

    response = client.post(

        "/ml-expert/anomaly",

        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] == True

    assert "anomaly_status" in data