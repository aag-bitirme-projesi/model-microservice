from utils.models import Model, User, DevelopersModel, UserDatasets
from utils.docker_service import DockerService
from flask import jsonify
import requests
from utils.database import db
from utils.storage import get_s3_ayca, StorageService
import uuid
import os
from datetime import datetime

class ModelService():
    
    def __init__(self):
        self.docker_service = DockerService()
        self.s3_service = StorageService()
    
    def list_users(self):
        return jsonify(User.query.all())

    def upload_model(self, model_dto, images):
        username = model_dto['username']
        modelName = model_dto['name']
        dockerImage = model_dto['dockerImage']
        price = model_dto["price"]
        description = model_dto["description"]
        
        keyname = f'{username}\{modelName}'
        model = Model(dockerImage, keyname, price, description)
        db.session.add(model)
        db.session.commit()
        
        user = User.query.filter_by(username=username).first()
        if user:
            developers_model = DevelopersModel(user.username, model.id)
            db.session.add(developers_model)
            db.session.commit()
        else:
            db.session.rollback()
            return jsonify("FAIL")
            
        for image in images:
            self.s3_service.upload_model_image(keyname, image)
            
        return jsonify(model)
    
    def list_models(self):
        return jsonify(Model.query.all())
        
    def list_models_by_username(self, username):
        models =  Model.query.join(DevelopersModel, Model.id == DevelopersModel.model_id) \
            .join(User, User.username == DevelopersModel.user_id) \
                .filter(User.username == username).all()
        return jsonify(models)
    
    def get_model_images(self, model_dto):
        username = model_dto['username']
        modelName = model_dto['name']
        
        keyname = f'{username}\{modelName}'
        return jsonify(self.s3_service.get_model_images(keyname))

    def remove_model(self, model_dto):
        username = model_dto['username']
        modelName = model_dto['name']
        
        keyname = f'{username}\{modelName}'
        
        user = User.query.filter_by(username = username).first()
        if not user:
            raise ValueError(f"User with username {username} not found")
        
        model = Model.query.filter_by(name = keyname).first()
        temp = model.copy()
        if not model:
            raise ValueError(f"Model with key {keyname} not found")
        
        developers_model = DevelopersModel.query.filter_by(user_id=user.username, model_id=model.id).first()
        if not developers_model:
            raise RuntimeError("Trust me, I am an Engineer !")
        
        db.session.delete(developers_model)
        db.session.delete(model)
        db.session.commit()
        
        return jsonify(temp)
        
    def run_model(self, model_dto):
        username = model_dto['username']
        modelName = model_dto['name']
        
        keyname = f'{username}\{modelName}'
        
        model = Model.query.filter_by(name = keyname).first()
        if not model:
            raise ValueError(f"User with username {username} not found")
        docker_image = model.model_link
        
        id, port = self.docker_service.run_docker_container(docker_image)
        return jsonify({'containerId': id, 
                        'port': port
                        })
    
    def close_container(self, data):
        container_id = data['containerId']
        
        self.docker_service.stop_docker_container(container_id)
        self.docker_service.remove_docker_container(container_id)
        return jsonify("SUCCESS")
        
    def upload_dataset(self, datasetDto):
        username = datasetDto["username"]
        dataset_name = datasetDto["dataset_name"]
        dataset_folder = datasetDto["dataset_folder"]
        folder_name = dataset_folder.split("/")[-1]

        S3_BUCKET_NAME = 'final-datasets1'
        new_folder = str(uuid.uuid1()) 
        get_s3_ayca().put_object(Bucket=S3_BUCKET_NAME, Key=new_folder + '/')
        
        for root, dirs, files in os.walk(dataset_folder):
            for file in files:
                if str(file) == ".DS_Store":
                    continue 
                file_path = os.path.join(root, file)
                f = file_path.split(folder_name)[-1]
                # Upload each file to S3
                s3_key = file_path.replace(dataset_folder, new_folder)  # Use relative path as S3 key
                
                path = new_folder + f
                print(path)
                get_s3_ayca().upload_file(file_path, S3_BUCKET_NAME, path)
                
        dataset = UserDatasets(username, dataset_name, dataset_folder, datetime.today())
        return jsonify(dataset)
    
    def get_my_datasets(self, username):
        return jsonify(UserDatasets.query.filter(UserDatasets.username==username))
    
    def delete_datasets(self, ids):
        try:
            db.session.query(UserDatasets).filter(UserDatasets.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            return "success"
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
        finally:
            db.session.close()