from flask import Flask, request, jsonify, Blueprint
from dotenv import load_dotenv
from utils.database import init_db
import os

from utils.model_service import ModelService

model_bp = Blueprint('model', __name__)
model_service = ModelService()

@model_bp.route('/upload-model', methods=['POST'])
def upload_model():
    data = request.form
    images = request.files.getlist('files')
    return model_service.upload_model(data, images)

@model_bp.route('/all', methods=['GET'])
def all():
    return model_service.list_models()

@model_bp.route('/remove-model', methods=['DELETE'])
def remove_model():
    data = request.form
    return model_service.remove_model(data)

@model_bp.route('/open-container', methods=['POST'])
def run_model():
    data = request.form
    return model_service.run_model(data)

@model_bp.route('/close-container', methods=['GET'])
def close_container():
    data = request.form
    return model_service.close_container(data)

@model_bp.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    data = request.form
    return model_service.upload_dataset(data)

# TODO
# TRAIN MODEL
# FUCK THIS SHIT ALSO