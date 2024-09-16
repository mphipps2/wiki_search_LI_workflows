import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from backend.src.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_endpoint():
    with client.websocket_connect("/ws/query/") as websocket:
        # Send a test query
        query = "Test query"
        websocket.send_text(query)

        # Receive the response
        response = websocket.receive_json()

        # Validate the response structure
        assert "response" in response
        assert "reasoning" in response
        assert "sources" in response

        # Additional checks can be added based on expected behavior
        assert response["response"] is not None
        assert isinstance(response["reasoning"], list)
        assert isinstance(response["sources"], list)