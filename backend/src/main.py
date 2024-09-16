from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import logging
from llama_index.llms.openai import OpenAI

from src.agents import ReActAgent
from src.utils import get_context
from src.observability import instrument
from src.tools import similar_articles_tool, full_article_tool
from llama_index.core.tools import ToolSelection, ToolOutput
from llama_index.core.agent.react.types import (
    ActionReasoningStep,
    ObservationReasoningStep,
)
import json
# Define a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Call Phoenix instrumentation
instrument()

MODEL = "gpt-4o"

logger.info("agent initialized")

@app.websocket("/ws/query/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Create a new instance of ReActAgent for this WebSocket session
    agent = ReActAgent(
        llm=OpenAI(model=MODEL), tools=[similar_articles_tool, full_article_tool], timeout=120, verbose=True, max_reasoning_steps=10
    )
    logger.info("New agent created for WebSocket session")

    try:
        # Process multiple queries within this WebSocket session
        while True:
            # Receive each query after connection is established
            query = await websocket.receive_text()

            try:
                # Run the agent with the query
                response = await agent.run(input=query)

                # Convert ToolOutput objects to JSON-serializable format
                response_serializable = {
                    "response": response.get("response"),
                    "reasoning": [reasoning.to_dict() if hasattr(reasoning, 'to_dict') else str(reasoning) for reasoning in response.get("reasoning", [])],
                    "sources": [source.to_dict() if hasattr(source, 'to_dict') else str(source) for source in response.get("sources", [])],
                }

                # Send all data at once
                await websocket.send_json(response_serializable)

            except Exception as e:
                logger.error(f"Error occurred: {str(e)}")
                await websocket.send_json({"type": "error", "data": "Internal server error"})
                await websocket.close()

    except WebSocketDisconnect:
        logger.info("Client disconnected, closing WebSocket session")

