from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import (
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    MINIO_URL,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
)
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from minio import Minio
from datetime import datetime
import uuid, os, tempfile

app = Flask(__name__)
app.config.from_object("config")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

# Minio configuration
app.config["MINIO_URL"] = MINIO_URL
app.config["MINIO_ACCESS_KEY"] = MINIO_ACCESS_KEY
app.config["MINIO_SECRET_KEY"] = MINIO_SECRET_KEY

db = SQLAlchemy(app)

# Set up user sessions
from app.models import User

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

minio_client = Minio(app.config["MINIO_URL"], app.config["MINIO_ACCESS_KEY"], app.config["MINIO_SECRET_KEY"], secure=True)

def generate_unique_object_name():
    # Generate a random UUID to ensure uniqueness
    unique_id = str(uuid.uuid4())

    object_name = f"{unique_id}.jpg"  # You can use any file extension you prefer

    return object_name

def save_picture_minio(temp_path):
    if not temp_path:
        return ''  # Return an empty string if no picture is provided

    try:
        # Generate a unique object name (e.g., based on timestamp or a UUID)
        object_name = generate_unique_object_name()  # Implement this function as needed

        # Upload the picture to Minio
        minio_client.fput_object(
            bucket_name="testing",  # Replace with your bucket name
            object_name=object_name,
            file_path=temp_path,
        )

        # Construct the public URL for the uploaded picture (no expiration)
        # picture_url = f"{app.config['MINIO_URL']}/{object_name}"
        picture_url = minio_client.presigned_get_object(
            bucket_name="testing",  # Replace with your bucket name
            object_name=object_name,
        )
        return picture_url

    except Exception as err:
        print(f"Minio error: {err}")
        return ''


from app import routes
