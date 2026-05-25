from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


#test document search

def test_document_search():

    payload = {

        "query": "What is refund policy?"
    }

    response = client.post(

        "/document-assistant/search",

        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] == True

    assert "answer" in data