import unittest
from faker import Faker
from ..modelos.modelos import Video, User, db
from ..vistas.vistas import VistaVideos
from flaskr import create_app
from ..app import app

class Test_listarVideos(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            self.data_factory = Faker()
            self.user = User(username='prueba_video', password='UniPass.2024', email='prueba@gmail.com')
            self.video1 = Video(name = self.data_factory.unique.name(),
                            path = self.data_factory.unique.name()
                            )
            self.video2 = Video(name = self.data_factory.unique.name(),
                            path = self.data_factory.unique.name()
                            )
            self.user.videos.append(self.video1)
            self.user.videos.append(self.video2)
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id

            self.video1_dict = {
                'name': self.video1.name,
                'path': self.video1.path
            }
            self.video2_dict = {
                'name': self.video2.name,
                'path': self.video2.path
            }
    
    def test_listar_videos(self):
        response = self.app.get('/api/videos')
        videos = response.get_json()
        dic_video1 = {
            'name': videos[-2]["name"],
            'path': videos[-2]["path"]
        }
        dic_video2 = {
            'name': videos[-1]["name"],
            'path': videos[-1]["path"]
        }
        self.assertEqual(self.video1_dict, dic_video1)
        self.assertEqual(self.video2_dict, dic_video2)
    def tearDown(self):
        Usuario_agregado = db.session.query(User).filter(User.id == self.user_id).first() 
        if Usuario_agregado:
            db.session.delete(Usuario_agregado)
            db.session.commit()
        db.session.close()
        