import jwt  # Importa la librería JWT
import datetime  # Para manejar la expiración del token
from flask_restful import Resource
from ..modelos import db, Video, VideoSchema, User, UserSchema, State, Task, TaskSchema
from flask import request, redirect, url_for, render_template, Flask, jsonify
import requests
import os
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "projectomiso-3e6a4576df92.json"
print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

video_schema = VideoSchema()
user_schema = UserSchema()
task_schema = TaskSchema()

SECRET_KEY = 'mi_secreto'  

class VistaVideos(Resource):
    
    def get(self):
        return [video_schema.dump(video) for video in Video.query.all()]

class VistaUsers(Resource):
    
    def get(self):
        return [user_schema.dump(user) for user in User.query.all()]
    
    def post(self):
        # Validar los datos de entrada (incluyendo password2)
        if not request.json or not all(k in request.json for k in ('username', 'password', 'password2', 'email')):
            return {'message': 'Missing fields'}, 400
        
        # Verificar que password y password2 sean iguales
        if request.json['password'] != request.json['password2']:
            return {'message': 'Passwords do not match'}, 400
        
        new_user = User(username=request.json['username'],
                        password=request.json['password'],
                        email=request.json['email'])
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return user_schema.dump(new_user), 201
        except Exception as e:
            return {'message': str(e)}, 400

class VistaUser(Resource):
    user_id = 0
    def post(self):
        # Buscar al usuario por username y password
        datos = request.get_json()
        user = User.query.filter_by(username=datos.get('username'), password=datos.get('password')).first()
        VistaUser.user_id = user.id
        
        if user is None:
            return {'message': 'User not found or invalid credentials'}, 404
        
        token = jwt.encode({
            'user_id': user.id,  # Incluye el id del usuario en el token
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiración en 1 hora
        }, SECRET_KEY, algorithm='HS256')
        
        # Devolver el usuario y el token
        return {
            'user': user_schema.dump(user),
            'token': token
        }, 200
def token_requerido(f):
    def wrap(*args, **kwargs):
        token = None
        # Verifica si el token está en el encabezado de autorización
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Elimina "Bearer" y solo toma el token
        
        if not token:
            return {'message': 'Token es requerido'}, 401
        
        try:
            # Intenta decodificar el token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return {'message': 'Token inválido'}, 401
        # Si el token es válido, pasa al siguiente controlador
        return f(*args, **kwargs)

    return wrap



class VistaTask(Resource):
    user_id = 0
    
    def extensiones_permitidas(filename):
        
        EXTENSIONES = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONES
    
    @token_requerido
    def post(self):  
        client = storage.Client()
        BUCKET_NAME = "miso-vinilos-jh"
        FOLDER_CARGA = 'videos'
        nombre_video = ''
        bucket = client.get_bucket(BUCKET_NAME)
        if not os.path.exists(FOLDER_CARGA):
            os.makedirs(FOLDER_CARGA)
        for campo, file in request.files.items():
            print(file)
            nombre_video += file.filename

        if nombre_video == '':
            return {'message': 'Por favor cargue un archivo'}, 400
        else:

            # Verifica si el archivo tiene una extensión permitida
            if VistaTask.extensiones_permitidas(nombre_video):
                path_video=os.path.join(FOLDER_CARGA, nombre_video)
                blob = bucket.blob(path_video)
                file.save(path_video)  # Guarda el archivo
                blob.upload_from_filename(path_video)
                file_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{path_video}"
                nueva_task = Task(
                    state = "UPLOADED",
                    name = nombre_video
                )
                db.session.add(nueva_task)
                db.session.commit()
                task = db.session.query(Task).filter(Task.id == nueva_task.id).first()
                response = requests.post("http://127.0.0.1:5001/tasks/add", json={"video":file_url,"id":task.id})
                
                data = response.json()

                
                try:
                    
                    

                    nuevo_video = Video(
                        name = nombre_video,
                        path = path_video,
                        duracion_original = VistaTask.duracion_video(path_video),
                        user_id = VistaUser.user_id,
                        task_id = task.id
                    )
                
                    db.session.add(nuevo_video)
                    db.session.commit()
                    return video_schema.dump(nuevo_video), 201
                    
                except Exception as e:
                    return {'message': str(e)}, 400

            else:
                return {'message': 'Extensión inválida'}, 300
            
    def duracion_video(path):
        with VideoFileClip(path) as video:
            duración = video.duration
            return duración
    
    @token_requerido
    def get(self):
        max_results = request.args.get('max', type=int)
        order = request.args.get('order', type=int, default=0)
        
        # Aplica orden ascendente o descendente
        if order == 1:
            query = Task.query.order_by(Task.id.desc()).all()
        else:
            query = Task.query.order_by(Task.id.asc()).all()
        
        # Limita el número de resultados
        if max_results:
            query = query.limit(max_results)
        
        return [task_schema.dump(task) for task in query], 200
        
        
class VistaTasks(Resource):
    @token_requerido
    def delete(self,id_task):
        video = Video.query.filter_by(id=id_task).first()
        db.session.delete(video)
        db.session.commit()
        respuesta = {
            "message":"Tarea eliminada",
            "id":id_task
        }
        return respuesta, 201
    
    @token_requerido
    def get(self, id_task):
        user_id = VistaUser.user_id
        task = Task.query.filter_by(id=id_task).first()
        
        if not task:
            return {'message': 'Tarea no encontrada'}, 404
        
        response = video_schema.dump(task)
        
        # Proporciona la URL del video procesado si está disponible
        if task.state == State.PROCESSED:
            url = url_for('static', filename=f'videos/{task.name.split(".")[0]}_procesado.{task.name.split(".")[1]}', _external=True)
            response['processed_video_url'] = url
        else:
            response['processed_video_url'] = None
        
        return response, 200
    
    
    

