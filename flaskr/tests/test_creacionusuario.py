import unittest
from faker import Faker
from ..modelos.modelos import User, db
from flaskr import create_app
from ..app import app

class Test_creacionUsuario(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()  # Crea las tablas en la base de datos en memoria
            self.data_factory = Faker()  # Instancia para generar datos ficticios
            # Datos de prueba para crear un usuario
            self.user_data = {
                "username": "usuario_prueba",
                "password": "UniPass.2024",
                "password2": "UniPass.2024",  # Se asegura que password y password2 coincidan
                "email": "usuario_prueba@gmail.com"
            }

    def test_creacion_usuario(self):
        # Crear un usuario a través de la API y validar la respuesta
        response = self.app.post('/api/auth/signup', json=self.user_data)
        self.assertEqual(response.status_code, 201)  # Validar que la creación fue exitosa

        # Verificar que el usuario fue agregado a la base de datos
        with app.app_context():
            usuario_agregado = User.query.filter_by(username=self.user_data['username']).first()
            self.assertIsNotNone(usuario_agregado)  # Verificar que el usuario fue creado
            self.assertEqual(usuario_agregado.email, self.user_data['email'])  # Comparar el email

    def test_fallo_passwords_no_coinciden(self):
        # Caso donde los passwords no coinciden
        invalid_user_data = self.user_data.copy()
        invalid_user_data['password2'] = "DiferentePass"  # Hacer que los passwords no coincidan

        response = self.app.post('/api/auth/signup', json=invalid_user_data)
        self.assertEqual(response.status_code, 400)  # Debe fallar
        self.assertIn('Passwords do not match', response.json['message'])  # Verificar el mensaje de error

    def tearDown(self):
        # Limpieza: eliminar el usuario agregado si existe
        with app.app_context():
            usuario_agregado = User.query.filter_by(username=self.user_data['username']).first()
            if usuario_agregado:
                db.session.delete(usuario_agregado)
                db.session.commit()

if __name__ == '__main__':
    unittest.main()
