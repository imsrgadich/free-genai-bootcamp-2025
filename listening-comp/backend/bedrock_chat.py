import boto3
import json
from typing import List, Dict, Optional
from datetime import datetime

class BedrockChat:
    def __init__(
        self,
        model_id: str = "amazon.nova-micro-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        region_name: Optional[str] = None
    ):
        """
        Initialize Bedrock Chat client.
        
        Args:
            model_id: Bedrock model ID
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens in response
            region_name: AWS region name (optional)
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = boto3.client('bedrock-runtime', region_name=region_name)
        self.conversation_history = []

    def _format_message(self, message: str) -> Dict:
        """Format message for Nova model."""
        return {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": self.temperature,
            "maxTokenCount": self.max_tokens,
            "stopSequences": [],
            "topP": 0.9
        }

    def chat(self, message: str) -> str:
        """
        Send a message to the model and get response.
        
        Args:
            message: User input message
            
        Returns:
            str: Model's response
        """
        try:
            # Prepare request body
            body = json.dumps(self._format_message(message))

            # Call the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )

            # Update response parsing for Nova model
            response_body = json.loads(response.get('body').read())
            response_text = response_body.get('generation', '')

            # Store in conversation history
            self._add_to_history(message, response_text)

            return response_text

        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            print(error_msg)
            return error_msg

    def _add_to_history(self, user_message: str, bot_response: str) -> None:
        """Add conversation to history with timestamp."""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response
        })

    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history."""
        return self.conversation_history

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def update_settings(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> None:
        """Update model settings."""
        if temperature is not None:
            self.temperature = max(0.0, min(1.0, temperature))
        if max_tokens is not None:
            self.max_tokens = max_tokens


# Example usage:
if __name__ == "__main__":
    # Initialize chat client
    chat_client = BedrockChat(
        temperature=0.7,
        max_tokens=1000
    )

    # Example conversation
    response = chat_client.chat("What are the main AWS services for AI/ML?")
    print(f"Response: {response}")

    # Get conversation history
    history = chat_client.get_conversation_history()
    print("\nConversation History:")
    for entry in history:
        print(f"Time: {entry['timestamp']}")
        print(f"User: {entry['user_message']}")
        print(f"Bot: {entry['bot_response']}\n")