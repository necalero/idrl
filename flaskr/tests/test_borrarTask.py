import unittest
from faker import Faker
from ..modelos.modelos import Video, User, db
from ..vistas.vistas import VistaVideos
from flaskr import create_app
from ..app import app

class Test_borrarTask(unittest.TestCase):

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
            login = {
                "username":self.user.username,
                "password":self.user.password
            }
            return_login = self.app.post('/api/auth/login', json=login)
            self.token = return_login.json["token"]
    
    def test_borrar_videos(self):
        videos = User.query.all()[-1].videos
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.delete(f'/api/tasks/{videos[1].id}', headers=headers)
        self.assertEqual(response.status_code, 201)

        video_after_delete = Video.query.get(videos[1].id)
        self.assertIsNone(video_after_delete)
    def tearDown(self):
        Usuario_agregado = db.session.query(User).filter(User.id == self.user_id).first() 
        if Usuario_agregado:
            db.session.delete(Usuario_agregado)
            db.session.commit()