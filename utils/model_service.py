from utils.models import Model, User, DevelopersModel, UserDatasets
from utils.docker_service import DockerService
from flask import jsonify, send_file
import requests
from utils.database import db
from utils.storage import get_s3_ayca, StorageService
import uuid
import os
from datetime import datetime

import json

from sqlalchemy.inspection import inspect

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
    
    def update_model(self, model_dto, images):
        username = model_dto['username']
        modelName = model_dto['name']
        dockerImage = model_dto['dockerImage']
        price = model_dto["price"]
        description = model_dto["description"]
        
        keyname = f'{username}\{modelName}'
        model = Model.query.filter_by(name = keyname).first()
        if not model:
            raise ValueError(f"Model with key {keyname} not found")
        model.dockerImage = dockerImage if dockerImage else model.dockerImage
        model.price = price if price else model.price
        model.description = description if description else model.description
        db.session.commit()
        
        for image in images:
            self.s3_service.upload_model_image(keyname, image)
        
        return jsonify(model)
    
    def list_models(self):
        models = Model.query.all()
        temp = []
        for model in models:
            images = self.s3_service.get_model_images(model.name)
            model_dict = {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
            print(type(model_dict))
            model_dict['images'] = images
            print(model_dict)
            temp.append(model_dict)
        return jsonify(temp)
    
    def by_id(self, id):
        model = Model.query.filter_by(id = id)
        image = self.s3_service.get_model_images(model.name)
        model_dict = {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
        model_dict['images'] = image

        return jsonify(model_dict)

    def list_models_by_username(self, username):
        models =  Model.query.join(DevelopersModel, Model.id == DevelopersModel.model_id) \
            .join(User, User.username == DevelopersModel.user_id) \
                .filter(User.username == username).all()
        return jsonify(models)
    
    def get_model_images(self, model_dto):
        username = model_dto['username']
        modelName = model_dto['name']
        
        keyname = f'{username}\{modelName}'
        print(keyname)
        print(self.s3_service.get_model_images(keyname))
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
            raise ValueError(f"Model with keyname {keyname} not found")
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
        
    # def upload_dataset(self, datasetDto):
    #     username = datasetDto["username"]
    #     dataset_name = datasetDto["dataset_name"]
    #     dataset_folder = datasetDto["dataset_folder"]
    #     folder_name = dataset_folder.split("/")[-1]

    #     S3_BUCKET_NAME = 'final-datasets1'
    #     new_folder = str(uuid.uuid1()) 
    #     get_s3_ayca().put_object(Bucket=S3_BUCKET_NAME, Key=new_folder + '/')
        
    #     for root, dirs, files in os.walk(dataset_folder):
    #         for file in files:
    #             if str(file) == ".DS_Store":
    #                 continue 
    #             file_path = os.path.join(root, file)
    #             f = file_path.split(folder_name)[-1]
    #             # Upload each file to S3
    #             s3_key = file_path.replace(dataset_folder, new_folder)  # Use relative path as S3 key
                
    #             path = new_folder + f
    #             print(path)
    #             get_s3_ayca().upload_file(file_path, S3_BUCKET_NAME, path)
                
    #     dataset = UserDatasets(username, dataset_name, dataset_folder, datetime.today())
    #     return jsonify(dataset)

    def upload_dataset(self, username, dataset_name, files):
        S3_BUCKET_NAME = 'final-datasets1'
        new_folder = uuid.uuid4().hex
        
        with open('temp.csv', 'w+', encoding="utf-8") as f:
            for file in files:
                root, dir, filename = os.path.normpath(file.filename).split(os.sep)
                new_obj = uuid.uuid4().hex
                get_s3_ayca().upload_fileobj(file, S3_BUCKET_NAME, new_obj)
                f.write(f"{filename},{dir},{new_obj}\n")
        
        with open('temp.csv', 'rb') as f:
            get_s3_ayca().upload_fileobj(f, S3_BUCKET_NAME, new_folder)
            
        os.remove('temp.csv')
        
        dataset = UserDatasets(username=username, dataset_name=dataset_name, file_id=new_folder, created_at=datetime.today())
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify(dataset)
    
        # S3_BUCKET_NAME = 'final-datasets1'
        # new_folder = str(uuid.uuid1()) 
        # get_s3_ayca().put_object(Bucket=S3_BUCKET_NAME, Key=new_folder + '/')

        # for file in files:
        #     # Maintaining the directory structure
        #     file_path = file.filename
        #     print("file path: ", file_path)
        #     s3_key = os.path.join(new_folder, file_path)
        #     get_s3_ayca().upload_fileobj(file, S3_BUCKET_NAME, s3_key)
        #     # get_s3_ayca().upload_file(file_path, S3_BUCKET_NAME, path)

        # dataset = UserDatasets(username=username, dataset_name=dataset_name, file_id=new_folder, created_at=datetime.today())
        # db.session.add(dataset)
        # db.session.commit()

        # return jsonify(dataset)
    
    def get_my_datasets(self, username):
        datasets = UserDatasets.query.filter(UserDatasets.username == username).all()
        print("datasets: ", datasets)
        # datasets_list = [dataset.to_dict() for dataset in datasets]
        return jsonify(datasets)
    
    def get_dataset(self, username, dataset_name):
        S3_BUCKET_NAME = 'final-datasets1'
        
        # Retrieve the file_id from the UserDatasets table
        dataset = UserDatasets.query.filter_by(username=username, dataset_name=dataset_name).first()
        file_id = dataset.file_id
        
        get_s3_ayca().download_file(S3_BUCKET_NAME, file_id, 'temp.csv')
        
        with open('temp.csv', 'r', encoding="utf-8") as f:
            lines = f.readlines()
    
        os.remove('temp.csv')
        
        with open('temp.csv', 'w+', encoding="utf-8") as f:
            for line in lines:
                if len(line.strip().split(',')) != 3:
                    continue
                
                filename, label, image_id = line.strip().split(',')
                url = get_s3_ayca().generate_presigned_url('get_object', 
                                                             Params = {'Bucket': S3_BUCKET_NAME, 
                                                                       'Key': image_id,
                                                                       'ResponseContentType': 'image/jpg'}, 
                                                             ExpiresIn = 30 * 24 * 60 * 60
                                                             )
                f.write(f"{filename},{label},{url}\n")
                
        return send_file('temp.csv', as_attachment=True)
        
    
    def delete_datasets(self, ids):
        try:
            ids = json.loads(ids)
            print(ids)
            db.session.query(UserDatasets).filter(UserDatasets.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            return "success"
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
        finally:
            db.session.close()
            
        return jsonify('SUCCESS')