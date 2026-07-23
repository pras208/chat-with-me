# Bedrock Flask Demo

A minimal Flask application that provides a web UI to enter a prompt, sends it to Amazon Bedrock, and displays the model's response.

## Project structure
```
bedrock-flask-demo/
├─ app.py                # Flask app, Bedrock client
├─ config.yaml           # AWS configuration (region, profile, model ID)
├─ requirements.txt      # Python dependencies
├─ .gitignore            # Ignored files
├─ templates/
│   └─ index.html       # Simple UI
└─ README.md             # This file
```

## Prerequisites
- Python 3.9+ installed
- AWS credentials configured (either default or a named profile). If you use a named profile, set its name in `config.yaml` under `aws.profile`.
- An Amazon Bedrock model ID you have access to (e.g., `anthropic.claude-v2`).

## Setup
```bash
# Clone the repository (if applicable) and cd into the directory
# git clone <repo-url>
# cd bedrock-flask-demo

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration
Edit **config.yaml** to match your environment:
```yaml
aws:
  region: us-east-1          # AWS region where Bedrock is enabled
  profile: my-profile        # (optional) name of the profile in ~/.aws/credentials
  model_id: anthropic.claude-v2   # Bedrock model identifier
```
If you omit `profile`, the default AWS credentials chain will be used.

## Run the application
```bash
python app.py
```
The server will start on `http://0.0.0.0:5000`. Open a browser and navigate to that address. You should see a simple page where you can type a prompt and receive the model's response.

## How it works
1. **UI** (`templates/index.html`) collects a prompt and POSTs it to `/invoke`.
2. **Flask endpoint** (`/invoke`) reads the JSON payload, builds a request body for Bedrock, and calls `bedrock-runtime.invoke_model` via **boto3**.
3. The response is parsed and returned to the UI, which displays it.

## Notes
- The payload format shown works for Claude‑style models. For other models you may need to adjust the JSON structure according to the model's API contract.
- In production, disable Flask's debug mode and consider adding proper error handling, logging, and HTTPS.
- The `.gitignore` file excludes `config.yaml` and other sensitive files from version control.

## License
This example is provided for educational purposes and is not intended for production use without proper security reviews.
