from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


#Test agent

def test_agent_chat():

    payload = {

        "query": "What products are trending?"
    }

    response = client.post(

        "/data-analyst/chat",

        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] == True

    assert "answer" in data