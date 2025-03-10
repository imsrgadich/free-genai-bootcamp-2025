# Hindi Language Listening Learning App

## Overview
The Hindi Language Listening Learning App is designed to enhance listening comprehension skills for learners of Hindi, similar to the JLPT5 format for Japanese. This app utilizes YouTube content to generate practice listening comprehension exercises, allowing users to immerse themselves in the language through authentic audio materials.

## Features
- **Listening Comprehension Exercises**: Practice with curated listening exercises based on real YouTube content.
- **Speech to Text (ASR)**: Optional integration with services like Amazon Transcribe or OpenWhisper for transcribing audio.
- **Text to Speech (TTS)**: Convert text to audio using services like Amazon Polly to aid in pronunciation and listening skills.
- **Interactive Frontend**: Built using Streamlit for an engaging user experience.

## Getting Started

### Prerequisites
- Ensure you have [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed on your machine.

### Creating the Conda Environment
To set up the project environment, follow these steps:

1. Open your terminal or command prompt.
2. Create a new conda environment named `listening-comp` with the latest stable version of Python:

   ```bash
   conda create -n listening-comp python=3.11
   ```

3. Activate the environment:

   ```bash
   conda activate listening-comp
   ```

4. Install the required packages from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Frontend Application

1. Navigate to the project directory:
   ```bash
   cd listening-comp
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run frontend/app.py
   ```

   The app will open automatically in your default web browser at `http://localhost:8501`

### Development

To run the app in development mode with auto-reload:
```bash
streamlit run app.py --server.runOnSave=true
```

## AWS Bedrock Setup

### Prerequisites
1. **AWS Account**: Ensure you have an AWS account with Bedrock access
2. **AWS CLI**: Install AWS CLI on your machine
3. **Python**: Python 3.8+ with pip installed

### Configuration Steps

1. **Configure AWS Credentials**
   ```bash
   aws configure
   ```
   Enter your credentials when prompted:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., us-east-1)
   - Output format (json)

2. **Install Required Packages**
   ```bash
   pip install boto3 python-dotenv
   ```

3. **Environment Setup**
   Create a `.env` file in project root:
   ```bash
   cp .env.example .env
   ```

4. **Update Environment Variables**
   ```ini
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=amazon.titan-text-express-v1 // <use model of your own choice>
   ```

### Usage Example
```python
import boto3

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'  # specify your region
)

# Example request body for Claude model
request = {
    "prompt": "Hello, how are you?",
    "max_tokens_to_sample": 300,
    "temperature": 0.5,
    "top_p": 1
}

response = bedrock_runtime.invoke_model(
    modelId='anthropic.claude-v2',  # or your chosen model
    body=json.dumps(request)
)
```

## Technical Requirements
- **YouTube Transcript API**: For downloading transcripts from YouTube videos.
- **Sqlite3**: To serve as a knowledge base for storing and retrieving data.
- **AWS Bedrock**: For AI/ML capabilities using Amazon's foundation models.
- **AI Coding Assistant**: Tools like Amazon Developer Q, Windsurf, Cursor, or GitHub Copilot for development assistance.
- **Guardrails**: Implementing safety measures to ensure the app operates within defined parameters.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
