import json
import requests
import subprocess
import os

def lambda_handler(event, context):
    """
    AWS Lambda handler that takes a user question and model name from the event,
    sends it to the Ollama API at localhost:11434/api/chat, and returns the answer.
    """
    # Start Ollama server and load model
    subprocess.run([f"{os.environ['LAMBDA_TASK_ROOT']}/entrypoint.sh"], shell=True)

    # Default values
    default_message = "What is the meaning of life?"
    default_model = "llama3.2:1b"

    # Parse the event body
    body = event.get("body")
    if body:
        try:
            body_data = json.loads(body)
            user_message = body_data.get("user_message", default_message)
            model_name = body_data.get("model_name", default_model)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON format in request body."})
            }
    else:
        user_message = default_message
        model_name = default_model

    # Construct request for Ollama
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False
    }

    # Send request to Ollama container
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    # Parse JSON response from Ollama
    try:
        data = response.json()
    except json.JSONDecodeError:
        data = {"response": response.text}

    # Return structured response
    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }
