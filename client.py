import asyncio
import websockets
import json
import re 


async def interactive_loop():
    """Run an interactive loop that prompts the user for queries and maintains the WebSocket connection."""
    
    print("Welcome to the Wikipedia Query CLI!")
    print("This tool allows you to query information from Wikipedia.")
    print("Ask me anything, or type 'exit' to quit.\n")

    uri = "ws://localhost:8000/ws/query/"

    # Establish a WebSocket connection only once
    async with websockets.connect(uri) as websocket:
        while True:
            # Prompt the user for input
            query = input("Enter your query (or type 'exit' to quit): ").strip()

            # Check if the user wants to exit
            if query.lower() == "exit":
                print("Goodbye!")
                await websocket.send("disconnect")  # Send a disconnect message to the server
                break

            # Send the query if the user didn't type 'exit'
            await send_query(query, websocket)

async def send_query(query: str, websocket):
    """Send the user's query to the FastAPI app and return the output."""
    
    # Send the query to the WebSocket
    await websocket.send(query)
    answer = None

    try:
        while True:
            response = await websocket.recv()
            if response:
                try:
                    data = json.loads(response)
                    # Extract and process the response
                    if "response" in data:
                        answer = data["response"]

                    # Extract and process the reasoning steps
                    if "reasoning" in data:
                        for thought in data["reasoning"]:
                            thought_match = re.search(r"thought='([^']*)'", thought)
                            if thought_match:
                                print(f"Thought: {thought_match.group(1)}")

                            # Extract action and action_input
                            if "action=" in thought:
                                action_part = thought.split("action=")[1]
                                action = action_part.split(" ")[0].strip("'")

                            if "action_input=" in thought:
                                action_input_part = thought.split("action_input=")[1]
                                action_input = action_input_part.split("}")[0] + "}"

                                # Extract the specific query term from action_input
                                query_match = re.search(r"'query': '([^']*)'", action_input)
                                if query_match:
                                    search_term = query_match.group(1)
                                    print(f"Action: Calling tool '{action}' and searching for '{search_term}'")

                    elif data["type"] == "error":
                        print("Error:", data["data"])
                except json.JSONDecodeError:
                    print("Received non-JSON response:", response)
            else:
                print("Received an empty response")

            # Print the final answer if received
            if answer is not None:
                print("\nAnswer:", answer)
                break
    except websockets.ConnectionClosed:
        print("Connection closed")


if __name__ == "__main__":
    asyncio.run(interactive_loop())
