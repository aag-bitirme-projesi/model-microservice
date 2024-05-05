from utils.database import db
from sqlalchemy import Column, Date, String, BigInteger, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PythonEnum
from dataclasses import dataclass

class Role(str, PythonEnum):
    ADMIN = 'ADMIN'
    USER = 'USER'

@dataclass
class User(db.Model):
    __tablename__ = 'users'

    username: str = Column(String, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    cv: str = Column(String(512))
    github: str = Column(String)
    payment_info: int = Column(BigInteger, ForeignKey('payment_infos.id'))
    role: "Role" = Column(Enum(Role), nullable=False)
    is_enabled: bool = Column(Boolean, default=True)

    def __init__(self, username, name, email, password, cv=None, github=None, payment_info=None, role=Role.USER):
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.cv = cv
        self.github = github
        self.payment_info = payment_info
        self.role = role
        self.is_enabled = True

    def get_id(self):
        return self.username

    def is_active(self):
        return self.is_enabled

@dataclass
class Model(db.Model):
    __tablename__ = 'models'

    id: int = Column(BigInteger, primary_key=True)
    model_link: str = Column(String(512))
    name: str = Column(String, name='model_name')

    def __init__(self, model_link, name):
        self.model_link = model_link
        self.name = name

@dataclass
class DevelopersModel(db.Model):
    __tablename__ = 'developers_models'

    id: int = Column(BigInteger, primary_key=True)
    developer: str = Column(String, ForeignKey('users.username'), nullable=False)
    model: int = Column(BigInteger, ForeignKey('models.id'), nullable=False)
    
    def __init__(self, user_id, model_id):
        self.developer = user_id
        self.model = model_id
        
@dataclass
class PaymentInfo(db.Model):
    __tablename__ = 'payment_infos'

    id: int = Column(BigInteger, primary_key=True)
    card_number: int = Column(Integer, nullable=False)
    cvc: int = Column(Integer, nullable=False)
    expiration_month: int = Column(Integer, nullable=False)
    expiration_year: int = Column(Integer, nullable=False)
    owner: str = Column(String, nullable=False)
    card_name: str = Column(String)

    def __init__(self, card_number, cvc, expiration_month, expiration_year, owner, card_name=None):
        self.card_number = card_number
        self.cvc = cvc
        self.expiration_month = expiration_month
        self.expiration_year = expiration_year
        self.owner = owner
        self.card_name = card_name

@dataclass
class Order(db.Model):
    __tablename__ = 'orders'

    id: int = Column(Integer, primary_key=True)
    order_date: datetime = Column(Date, default=datetime.utcnow)
    user: str = Column(String, ForeignKey('users.username'), name='_user', nullable=False)
    model_name: int = Column(BigInteger, ForeignKey('models.id'), nullable=False)
    
    def __init__(self, user_id, model_name_id):
        self.user_id = user_id
        self.model_name_id = model_name_id

@dataclass
class Payment(db.Model):
    __tablename__ = 'payments'

    id: int = Column(BigInteger, primary_key=True)
    username: int = Column(Integer, ForeignKey('users.username'), nullable=False)
    payment: int = Column(Integer, ForeignKey('payment_infos.id'), nullable=False)
    
    def __init__(self, user_id, payment_info_id):
        self.user_id = user_id
        self.payment_info_id = payment_info_id

@dataclass
class ModelImages(db.Model):
    __tablename__ = 'model_images'

    id: int = Column(BigInteger, primary_key=True)
    model_name: str = Column(String, nullable=False)
    image_id: str = Column(String, nullable=False)
    
    def __init__(self, model_name, image_id):
        self.model_name = model_name
        self.image_id = image_id

@dataclass
class UserDatasets(db.Model):
    __tablename__ = 'user_datasets'

    id: int = Column(BigInteger, primary_key=True)
    username: int = Column(Integer, ForeignKey('users.username'), nullable=False)
    dataset_name: str = Column(String, nullable=False)
    file_id: str = Column(String, nullable=False)


    def __init__(self, username, dataset_name, image_id):
        self.username = username
        self.dataset_name = dataset_name
        self.file_id = image_id