from fastapi.testclient import TestClient

from app.api.main import app
import os
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "test-deployment")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_EXPIRATION_SECONDS", "3600")
os.environ.setdefault("JWT_COOKIE_NAME", "access_token")

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DATABASE", "intelliretail_test")
os.environ.setdefault("MONGODB_DB_NAME", "intelliretail_test")

os.environ.setdefault("LANGCHAIN_API_KEY", "test-key")
os.environ.setdefault("LANGCHAIN_PROJECT", "test-project")

client = TestClient(app)


def test_root_api_running():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["message"] == "IntelliRetail AI API Running"


def test_login_missing_password_returns_422():
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com"
        },
    )

    assert response.status_code == 422


def test_signup_missing_email_returns_422():
    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "password": "secret123"
        },
    )

    assert response.status_code == 422


def test_agent_chat_without_login_returns_401():
    response = client.post(
        "/data-analyst/chat",
        json={
            "query": "What products are trending?"
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"


def test_document_search_without_login_returns_401():
    response = client.post(
        "/document-assistant/search",
        json={
            "query": "What is refund policy?"
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"


def test_forecast_without_login_returns_401():
    response = client.post(
        "/ml-expert/forecast",
        json={
            "quantity": 10,
            "profit": 250,
            "returns": 1,
            "order_year": 2025,
            "order_month": 11,
            "order_day": 15,
            "profit_margin": 22,
            "shipping_days": 3
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"


def test_anomaly_without_login_returns_401():
    response = client.post(
        "/ml-expert/anomaly",
        json={
            "sales": 10000,
            "profit": -5000,
            "quantity": 1,
            "profit_margin": -50,
            "shipping_days": 15
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"