import json
import yaml
import boto3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Set up basic logging to a file
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        # logging.StreamHandler()
    ]
)

# Load AWS configuration from config.yaml
with open('config.yaml', 'r') as cfg_file:
    cfg = yaml.safe_load(cfg_file)['aws']

region = cfg.get('region')
profile = cfg.get('profile')
model_id = cfg.get('model_id')

# Create a boto3 session respecting the optional profile
session_kwargs = {}
if profile:
    session_kwargs['profile_name'] = profile

session = boto3.Session(**session_kwargs)
bedrock_client = session.client('bedrock-runtime', region_name=region)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invoke', methods=['POST'])
def invoke_model():
    data = request.get_json()
    prompt = data.get('prompt', '')
    logging.info(f"Received prompt: {prompt}")
    if not prompt:
        logging.warning('Prompt missing in request')
        return jsonify({'error': 'Prompt is required'}), 400

    # Prepare payload for the Bedrock model (example for Claude style models)
    payload = {
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "text": prompt
                }
            ]
            }
        ],
        "inferenceConfig": {
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(payload).encode('utf-8'),
            contentType='application/json'
        )
        response_body = json.loads(response['body'].read())
        logging.info(f"Bedrock response: {response_body}")
        # Extract the text from the response for models that return a nested structure
        # Example response format:
        # {
        #   "output": {"message": {"content": [{"text": "..."}], "role": "assistant"}}
        # }
        text_response = None
        if isinstance(response_body, dict):
            # Try the nested path used by Amazon Nova model
            try:
                text_response = response_body['output']['message']['content'][0]['text']
            except Exception:
                # Fallback to other possible keys
                text_response = response_body.get('completion') or response_body.get('output')
        else:
            text_response = response_body
        logging.info(f"Returning extracted text: {text_response}")
        return jsonify({'response': text_response})
    except Exception as e:
        logging.error(f"Error invoking model: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Enable debug mode for development; remove in production
    app.run(host='0.0.0.0', port=5000, debug=True)
