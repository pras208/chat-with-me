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
inference_config = cfg.get('inference_config', {})

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

    # Build inference configuration with defaults and config overrides
    inference_params = {
        "temperature": inference_config.get('temperature', 0.7),
        "topP": inference_config.get('topP', 0.9)
    }
    
    # Add maxTokens if specified
    if 'maxTokens' in inference_config:
        inference_params['maxTokens'] = inference_config['maxTokens']
    
    # Add stopSequences if specified
    if 'stopSequences' in inference_config:
        inference_params['stopSequences'] = inference_config['stopSequences']

    try:
        # Use the Converse API - unified interface across all Bedrock models
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig=inference_params
        )
        
        # Extract response text using the standard Converse API structure
        text_response = response['output']['message']['content'][0]['text']
        logging.info(f"Bedrock response: {text_response}")
        
        return jsonify({'response': text_response})
    except Exception as e:
        logging.error(f"Error invoking model: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Enable debug mode for development; remove in production
    app.run(host='0.0.0.0', port=5000, debug=True)
