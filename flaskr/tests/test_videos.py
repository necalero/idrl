from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import unittest
from faker import Faker
from ..modelos.modelos import Video, User, db
from ..vistas.vistas import VistaTask
from flaskr import create_app
from ..app import app
from io import BytesIO
from flask_restful import Api

class Test_editarvideos(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            self.data_factory = Faker()
            self.user = User(username='prueba_video', password='UniPass.2024', email='prueba@gmail.com')
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            login = {
                "username":self.user.username,
                "password":self.user.password
            }
            return_login = self.app.post('/api/auth/login', json=login)
            self.token = return_login.json["token"]
    
    
    '''def test_cargar_videos(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        path = "flaskr/videos/pruebas.mp4"
        with open(path, 'rb') as f:

            file_data = FileStorage(stream=f, filename=secure_filename(path))


            response = self.app.post('/tasks', data={'file': file_data}, headers=headers)

        print(response)
'''



    def tearDown(self):
        Usuario_agregado = db.session.query(User).filter(User.id == self.user_id).first() 
        if Usuario_agregado:
            db.session.delete(Usuario_agregado)
            db.session.commit()