from utils.database import db
from utils.models import ModelImages, UserDatasets
import boto3
import uuid
import os

class StorageService:
    MODEL_IMAGES_BUCKET = 'model-images-storage'
    USER_DATASETS_BUCKET = 'user-datasets-storage'
    
    def __init__(self):
        self.client = boto3.client('s3', 
                                   aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), 
                                   aws_secret_access_key=os.getenv('AWS_SECRET_KEY'), 
                                   region_name=os.getenv('AWS_REGION'))
    
    def upload_model_image(self, model_name, file):
        image_id = uuid.uuid4().hex
        
        try:
            self.client.upload_fileobj(file, self.MODEL_IMAGES_BUCKET, image_id)
            model_images = ModelImages(model_name, image_id)
            db.session.add(model_images)
            db.session.commit()
            
            return True
        except Exception as e:
            return False
        
    def get_model_images(self, model_name):
        images = []
        try:
            model_images = ModelImages.query.filter_by(model_name=model_name).all()
            for model_image in model_images:
                url = self.client.generate_presigned_url('get_object', 
                                                         Params = {'Bucket': self.MODEL_IMAGES_BUCKET, 'Key': model_image.image_id}, 
                                                         ExpiresIn = 60 * 60)
                images.append(url)
            return images
        except Exception as e:
            print(e)
            return False
        
    def upload_user_dataset(self):
        raise NotImplementedError()
    
    def get_user_dataset(self):
        raise NotImplementedError()


def get_s3_ayca():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AYCA_AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AYCA_AWS_ACCESS_KEY'),
        region_name=os.getenv('AWS_ACCESS_KEY'),
    )
