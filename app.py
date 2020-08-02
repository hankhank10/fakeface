from flask import Flask, jsonify
import requests
import shutil
import cv2
import secrets
from pyagender import PyAgender
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

db.init_app(app)
migrate = Migrate(app, db)


class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    filename = db.Column(db.String(100))
    date_added = db.Column(db.DateTime)
    source = db.Column(db.String(100))

# settings
url = "https://thispersondoesnotexist.com/image"
male_threshold = 0.4
female_threshold = 0.6
temp_file = "temp_img.jpg"


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/download_face')
def download_face():
    # download face
    response = requests.get(url, stream=True)
    with open(temp_file, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    return "Downloaded to temporary file"


@app.route('/recognise_face')
def recognise_face():
    agender = PyAgender()

    faces = agender.detect_genders_ages(cv2.imread(temp_file))
    if len(faces) == 1:
        face = faces[0]
        gender_numeric = face['gender']
        age = int(face['age'])

        gender = "unclear"
        if gender_numeric < male_threshold: gender = "male"
        if gender_numeric > male_threshold: gender = "female"
    else:
        #face not detected or multiple faces detected
        gender = "unclear"
        age = 0

    return gender, age


@app.route('/generate_face')
def generate_face():
    download_face()
    gender, age = recognise_face()

    image_record = ImageRecord(
        gender=gender,
        age=age,
        filename="Test",
        date_added=datetime.utcnow())

    db.session.add(image_record)
    db.session.commit()

    location_to_move_to = "classified/" + gender + "_" + str(age) + "_" + secrets.token_hex(20) + ".jpg"
    shutil.move(temp_file, location_to_move_to)

    return gender


@app.route('/test')
def test():
    db_output = ImageRecord.query.first()
    dict_output = {
        'id': db_output.id,
        'gender': db_output.gender,
        'age': db_output.age,
        'filename': db_output.filename,
        'date_added': db_output.date_added
    }
    return jsonify(dict_output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11000, debug=True)
