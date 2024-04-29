from flask import Flask, request, jsonify
from dotenv import load_dotenv
from database import init_db
import os

from model_service import ModelService

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
init_db(app)

model_service = ModelService()

@app.route('/model')
def index():
    return 'Hello world'

@app.route('/upload-model', methods=['POST'])
def upload_model():
    data = request.form
    return model_service.upload_model(data)

@app.route('/all', methods=['GET'])
def all():
    return model_service.list_models()

@app.route('/remove-model', methods=['DELETE'])
def remove_model():
    data = request.form
    return model_service.remove_model(data)

@app.route('/run-model', methods=['POST'])
def run_model():
    data = request.form
    return model_service.run_model(data)

@app.route('/close-container', methods=['GET'])
def close_container():
    data = request.form
    return model_service.close_container(data)

if __name__ == '__main__':
    app.run(debug=True)
