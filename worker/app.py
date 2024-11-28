from flask import Flask, request, jsonify
from flask_migrate import Migrate
from celery import Celery
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from celery.result import AsyncResult
import os
from google.cloud import storage
from modelos import db, Video, VideoSchema, User, UserSchema, State, Task, TaskSchema

video_schema = VideoSchema()
user_schema = UserSchema()
task_schema = TaskSchema()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "projectomiso-3e6a4576df92.json"
print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@34.123.151.140/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
migrate = Migrate(app, db)
celery = Celery(
    'worker',
    broker='redis://127.0.0.1:6379/0', 
    backend='redis://127.0.0.1:6379/0'
)

celery.conf.update(
       result_backend='redis://localhost:6379/0',
    )

def duracion_video(path):
        with VideoFileClip(path) as video:
            duración = video.duration
            return duración
        
@celery.task(name="worker.edicion_video")
def edicion_video(url_video, task_id):
        try:
            client = storage.Client()
            BUCKET_NAME = "miso-vinilos-jh"
            
            bucket = client.get_bucket(BUCKET_NAME)
            
            #print(video)
            #video = VideoFileClip(path)
            nombre_video = ""
            FOLDER_CARGA = 'videos'
            if not os.path.exists(FOLDER_CARGA):
                        os.makedirs(FOLDER_CARGA)
        
            nombre_video = url_video.split('/')[-1]
            print("-a-aa-a-a-a")
            print(nombre_video)

            blob = bucket.blob(nombre_video)
            video_data = blob.download_as_bytes()
            with open("video_descargado.mp4", "wb") as video_file:
                video_file.write(video_data)
            
            #20 segundos
            #if duracion_video(path)>20:
            #with path_video as video1:
            video_saved = VideoFileClip("video_descargado.mp4")
            video_saved = video_saved.subclip(0,20)

            #aspecto 16:9
            video_saved = video_saved.resize((1280,720))
            nuevo_path=nombre_video.rsplit('.', 1)[0].lower()+"_procesado."+nombre_video.rsplit('.', 1)[1].lower()

            # Cargar imágenes

            logo = ImageClip("videos/logo.png").set_duration(3).resize(video_saved.size)


            # Crear el nuevo video

            video = concatenate_videoclips([logo, video_saved, logo])

            
            video.write_videofile(nuevo_path, codec='libx264', fps=24)
            blob = bucket.blob(nuevo_path)
            blob.upload_from_filename(nuevo_path)
            return task_id
        except Exception as e:
            print(f"Error en la tarea: {e}")
            raise
@celery.task
def post_edicion(task_id):
    try:
        print("postedicion")
        print(task_id)
        # Accede a la app Flask
        with app.app_context():
            task = db.session.query(Task).filter(Task.id == task_id).first()
            print(task)
            # Realiza las operaciones que necesiten contexto
            if task:
                task.state = "PROCESSED"
                db.session.add(task)
                db.session.commit()
            else:
                print(f"No se encontró la tarea con id {task_id}")
    except Exception as e:
        print(f"Error en la tarea post_edicion: {e}")
     
@app.route('/tasks/add', methods=['POST'])
def add_task():
    data = request.get_json()
    video_url = data['video']
    task_id = data['id']
    task = edicion_video.apply_async(args=[video_url,task_id], link=post_edicion.s())
    return jsonify({'task_id': task.id}), 202

@app.route('/tasks/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task_result = AsyncResult(task_id)
    print(task_result)
    return jsonify({
        'task_id': task_id,
        'state': task_result.state,       # Estado de la tarea
        'result': task_result.result      # Resultado si ha terminado
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)