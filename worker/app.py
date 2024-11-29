from flask import Flask, request, jsonify
from flask_migrate import Migrate
from celery import Celery
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from celery.result import AsyncResult
import os
import json
from google.cloud import storage
from google.cloud import pubsub_v1
from modelos import db, Video, VideoSchema, User, UserSchema, State, Task, TaskSchema

video_schema = VideoSchema()
user_schema = UserSchema()
task_schema = TaskSchema()

PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_NAME = os.getenv('TOPIC_NAME')
SUBSCRIPTION_NAME = os.getenv('SUBSCRIPTION_NAME')
DATABASE_URL = os.getenv('DATABASE_URL')
CREDENTIALS_BUCKET = os.getenv('CREDENTIALS_BUCKET')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC')
PUBSUB_SUBSCRIPTION = os.getenv('PUBSUB_SUBSCRIPTION')

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

def download_credentials(bucket_name, file_name, destination_path):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(destination_path)
    print(f"Credenciales descargadas a {destination_path}")

# Descargar credenciales desde Cloud Storage
download_credentials(CREDENTIALS_BUCKET, CREDENTIALS_FILE, '/tmp/credentials.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/credentials.json'
print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

app = Flask(__name__)

# Utiliza la URI de la base de datos desde las variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
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
    broker=os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0'), 
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
)

celery.conf.update(result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

def duracion_video(path):
    with VideoFileClip(path) as video:
        return video.duration

@celery.task(name="worker.edicion_video")
def edicion_video(url_video, task_id):
    try:
        client = storage.Client()
        BUCKET_NAME = os.getenv('VIDEO_BUCKET_NAME', 'idrl-videos')

        bucket = client.get_bucket(BUCKET_NAME)
        nombre_video = url_video.split('/')[-1]

        blob = bucket.blob(nombre_video)
        video_data = blob.download_as_bytes()
        with open("video_descargado.mp4", "wb") as video_file:
            video_file.write(video_data)

        video_saved = VideoFileClip("video_descargado.mp4").subclip(0, 20).resize((1280, 720))
        nuevo_path = f"{nombre_video.rsplit('.', 1)[0].lower()}_procesado.{nombre_video.rsplit('.', 1)[1].lower()}"

        logo = ImageClip("videos/logo.png").set_duration(3).resize(video_saved.size)
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
        with app.app_context():
            task = db.session.query(Task).filter(Task.id == task_id).first()
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

    message = {
        "video_url": video_url,
        "task_id": task_id
    }

    future = publisher.publish(topic_path, data=json.dumps(message).encode("utf-8"))
    return jsonify({"message_id": future.result()}), 202

@app.route('/tasks/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task_result = AsyncResult(task_id)
    return jsonify({
        'task_id': task_id,
        'state': task_result.state,
        'result': task_result.result
    })

def callback(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        edicion_video(data["video_url"], data["task_id"])
        message.ack()
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        message.nack()

def start_subscriber():
    subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

if __name__ == '__main__':
    start_subscriber()
    app.run(host='0.0.0.0', port=5001)
