#flaskr/app.py
from . import create_app
from .modelos import db, Video, User
from .modelos import VideoSchema
from flask_restful import Api
from flask_migrate import Migrate
from .vistas import VistaVideos, VistaUsers, VistaUser,  VistaTask, VistaTasks

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
migrate = Migrate(app, db)

#Initial Api

api = Api(app)
api.add_resource(VistaVideos, '/api/videos')
api.add_resource(VistaUsers, '/api/auth/signup')
api.add_resource(VistaUser, '/api/auth/login')
api.add_resource(VistaTasks, '/api/tasks/<int:id_task>')
api.add_resource(VistaTask, '/api/tasks')



# TEST BY VICTOR
# Crear un usuario y un video asociado formato JSON
#with app.app_context():
    # Crear el esquema de video para serialización
    #video_schema = VideoSchema()
    # Crear un usuario
    #user = User(username='vduarte', password='UniPass.2024', email='v.duarteq@uniandes.edu.co')
    # Crear un video asociado a ese usuario
    #video = Video(name='Python', path='1235535343hydsjhfsad')
    # Asociar el video al usuario usando la relación definida en el modelo
    #user.videos.append(video)
    # Guardar el usuario (y el video gracias a la relación)
    #db.session.add(user)
    #db.session.commit()
    # Imprimir los usuarios y los videos asociados
    #print(User.query.all())
    #print(User.query.all()[0].videos)
    # También puedes serializar los videos y mostrarlos
    #print([video_schema.dumps(video) for video in Video.query.all()])


#Create Videos and Users
#with app.app_context():
#    u = User(username='vduarte', password='UniPass.2024', email='v.duarteq@uniandes.edu.co')
#    v = Video(name='Python', path='1235535343hydsjhfsad')
#    u.videos.append(v)
#    db.session.add(u)
#    db.session.commit()
#    print(User.query.all())
#    print(User.query.all()[0].videos)



