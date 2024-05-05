import os
from flask import Flask
from dotenv import load_dotenv
from utils.database import init_db
from model_blueprint import model_bp

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
init_db(app)

app.register_blueprint(model_bp, url_prefix='/model')

if __name__ == '__main__':
    app.run(debug=True, port=2000)
    