#worker/modelos/modelos.py
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import datetime, enum

db = SQLAlchemy()

class State(enum.Enum):
    UPLOADED = "Uploaded"
    PROCESSED = "Processed"

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.String(256))
    duracion_original = db.Column(db.Double)
    duracion_tras_edicion = db.Column(db.Double)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # ForeignKey between User and Video
    rating = db.Column(db.Integer, nullable=True)
    fecha_carga = db.Column(db.DateTime, default=datetime.datetime.now())
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    # def __repr__(self):
    #     return "{},{},{}".format(self.id, self.name, self.path)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Enum(State), default=State.UPLOADED)
    name = db.Column(db.String(64))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(32))
    email = db.Column(db.String(32))
    videos = db.relationship('Video', cascade='all, delete, delete-orphan')

    # def __repr__(self):
    #     return "{},{},{}".format(self.id, self.username, self.password, self.email)


class VideoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Video
        include_relationships = True
        load_instance = True


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        load_instance = True
