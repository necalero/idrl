from flask import Flask

def create_app(config_name):
    app = Flask(__name__)


    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@34.123.151.140/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    return app