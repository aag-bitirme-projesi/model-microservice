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

    print("Received form data:", data)
    print("Received files:", images)

    return model_service.upload_model(data, images)

@model_bp.route('/update-model', methods=['POST'])
def update_model():
    data = request.form
    images = request.files.getlist('files')

    print("Received form data:", data)
    print("Received files:", images)

    return model_service.update_model(data, images)

@model_bp.route('/get-image', methods=['GET'])
def get_image():
    username = request.args.get('username')
    model_name = request.args.get('name')
    data = {'username': username, 'name': model_name}
    return model_service.get_model_images(data)

@model_bp.route('/all', methods=['GET'])
def all():
    return model_service.list_models()

@model_bp.route('/by-id', methods=['GET'])
def get_model_by_id():
    id = request.args.get('modelId')
    return model_service.by_id(id)

@model_bp.route('/remove-model', methods=['DELETE'])
def remove_model():
    data = request.form
    return model_service.remove_model(data)

@model_bp.route('/open-container', methods=['POST'])
def run_model():
    data = request.form
    return model_service.run_model(data)

@model_bp.route('/close-container', methods=['POST'])
def close_container():
    data = request.form
    return model_service.close_container(data)

@model_bp.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    data = request.form
    files = request.files.getlist('files')
    username = data.get('username')
    dataset_name = data.get('dataset_name')
    
    return model_service.upload_dataset(username, dataset_name, files)

@model_bp.route('/my-datasets', methods=['GET'])
def get_my_datasets():
    # data = request.form
    username = request.args.get('username')
    print("ussername: ", username)
    return model_service.get_my_datasets(username)

@model_bp.route('/delete-datasets', methods=['POST'])
def delete_datasets():
    data = request.form
    return model_service.delete_datasets(data["ids"])

@model_bp.route('/get-dataset', methods=['POST'])
def get_dataset():
    data = request.form
    username = data.get('username')
    dataset_name = data.get('dataset_name')
    return model_service.get_dataset(username, dataset_name)

# TODO
# TRAIN MODEL
# FUCK THIS SHIT ALSO