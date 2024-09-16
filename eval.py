import asyncio
import pandas as pd
from datasets import Dataset
from tqdm import tqdm
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import websockets
import json
from typing import Dict, List

# Load the DataFrame from the CSV file
test_df = pd.read_csv("./data/eval_queries/test_queries.csv", index_col=0)
model = "gpt-4o"
OUTPUT_FILE_FULL = f"./data/eval_results/test_queries_results_full-{model}.csv"
OUTPUT_FILE_REDUCED = f"./data/eval_results/test_queries_results_metrics_only-{model}.csv"


async def send_query_for_eval(query: str) -> Dict[str, List[str]]:
    """Send the user's query to the websocket app and return the output."""
    uri = "ws://localhost:8000/ws/query/"
    async with websockets.connect(uri, timeout=1000) as websocket:
        await websocket.send(query)
        answer = None
        context = []
        try:
            while True:
                response = await websocket.recv()
                if response:
                    try:
                        data = json.loads(response)

                        # Capture the final answer
                        if "response" in data:
                            answer = data["response"]

                        # Capture context from sources
                        if "sources" in data:
                            context = get_context(data)

                    except json.JSONDecodeError:
                        print("Received non-JSON response:", response)

                # Break when the answer has been received
                if answer is not None:
                    break
        except websockets.ConnectionClosed:
            print("Connection closed")
    
    return {"answer": answer, "contexts": context}

def get_context(response) -> list[str]:
    """Extract the context (Wikipedia sources) from the agent's response."""
    content = []
    for source in response['sources']:
        # Since source is always a string, add it directly
        content.append(source)
    return content


async def generate_response(question: str) -> dict:
    """Send a query to the ReAct agent and return the answer and context."""
    response = await send_query_for_eval(question)  # Use the new function
    return {
        "answer": response.get('answer'),
        "contexts": response.get('contexts'),
    }


async def generate_ragas_dataset(test_df: pd.DataFrame) -> Dataset:
    """Generate a dataset of agent responses and their contexts for evaluation."""
    test_questions = test_df["query"].values
    responses = []
    
    for question in tqdm(test_questions):
        response = await generate_response(question)  # Process each question serially
        responses.append(response)
    
    dataset_dict = {
        "question": test_questions,
        "response": [response["answer"] for response in responses],  # The agent's responses
        "contexts": [response["contexts"] for response in responses],  # Store contexts separately for each question
    }

    # Convert to Hugging Face Dataset
    return Dataset.from_dict(dataset_dict)


async def evaluate_ragas(test_df: pd.DataFrame):
    """Generate responses and evaluate using ragas metrics."""
    # Generate dataset from agent's responses
    ragas_eval_dataset = await generate_ragas_dataset(test_df.head(15))

    # Evaluate using faithfulness and answer relevancy metrics
    evaluation_result = evaluate(
        dataset=ragas_eval_dataset,
        metrics=[faithfulness, answer_relevancy],
    )

    # Convert evaluation results to a DataFrame for easier viewing
    eval_scores_df = pd.DataFrame(evaluation_result.scores)
    
    # Round the evaluation scores to the 3rd significant digit
    eval_scores_df = eval_scores_df.round(3)

    # Create the reduced DataFrame
    reduced_df = eval_scores_df.copy()

    # Add question, answer, and context columns
    eval_scores_df["question"] = ragas_eval_dataset["question"]
    eval_scores_df["response"] = ragas_eval_dataset["response"]
    eval_scores_df["contexts"] = ragas_eval_dataset["contexts"]

    reduced_df["question"] = ragas_eval_dataset["question"]
    reduced_df["response"] = ragas_eval_dataset["response"]

    # Add an average row at the end for both DataFrames
    avg_row_full = eval_scores_df.mean(numeric_only=True).round(3)
    avg_row_full["question"] = "Average"
    avg_row_full["response"] = ""
    avg_row_full["contexts"] = ""
    eval_scores_df = pd.concat([eval_scores_df, pd.DataFrame([avg_row_full])], ignore_index=True)

    avg_row_reduced = reduced_df.mean(numeric_only=True).round(3)
    avg_row_reduced["question"] = "Average"
    reduced_df = pd.concat([reduced_df, pd.DataFrame([avg_row_reduced])], ignore_index=True)

    # Save the full DataFrame with all information (question, response, contexts, faithfulness, answer_relevancy)
    eval_scores_df.to_csv(OUTPUT_FILE_FULL, index=False)

    # Save the reduced DataFrame (question and response)
    reduced_df.to_csv(OUTPUT_FILE_REDUCED, index=False)
    
    print("Evaluation Results (Full):")
    print(eval_scores_df)
    print("Evaluation Results (Reduced):")
    print(reduced_df)


if __name__ == "__main__":
    # Run the evaluation loop
    asyncio.run(evaluate_ragas(test_df))

