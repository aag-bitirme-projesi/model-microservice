import os
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy

class SQLAlchemy(BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True
        options["pool_recycle"] = 1800  # Recycle connections every 30 minutes
        options["pool_timeout"] = 30  # Wait 30 seconds for a connection from the pool
        options["pool_size"] = 10  # Maximum number of connections in the pool
        options["max_overflow"] = 5  # Maximum overflow connections
        

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 1800,  # Recycle connections every 30 minutes
        'pool_timeout': 30,    # Wait 30 seconds for a connection from the pool
        'pool_size': 10,       # Maximum number of connections in the pool
        'max_overflow': 5,     # Maximum overflow connections
        'connect_args': {
            'options': '-c statement_timeout=60000'  # Set a statement timeout of 60 seconds
        }
    }
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
