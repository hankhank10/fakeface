import requests
import shutil
import cv2
import secrets
from pyagender import PyAgender
import time
from datetime import datetime

from time import sleep

from active_alchemy import ActiveAlchemy

db = ActiveAlchemy('sqlite:///db.sqlite')

# settings
url = "https://thispersondoesnotexist.com/image"
male_threshold = 0.4
female_threshold = 0.6
temp_file = "temp_img.jpg"
times_to_run = 500
seconds_to_sleep = 2


class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)

    filename = db.Column(db.String(100))
    hosting = db.Column(db.String(100), default="local")

    def image_url(self):
        if self.hosting == "local":
            output = "https://fakeface.rest/to_be_uploaded_to_static_host/" + self.filename
        return output

    date_added = db.Column(db.DateTime)
    source = db.Column(db.String(100))

    last_served = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.DateTime)
    deleted_at = db.Column(db.Boolean)


def download_face():
    response = requests.get(url, stream=True)
    with open(temp_file, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return


def recoginise_face():
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


def move_file(gender, age):
    filename = gender + "_" + str(age) + "_" + secrets.token_hex(20) + ".jpg"
    location_to_move_to = "static/classified/" + filename
    shutil.move(temp_file, location_to_move_to)
    return filename


def write_db(gender, age, filename):
    image_record = ImageRecord(
        gender=gender,
        age=age,
        filename=filename,
        date_added=datetime.utcnow(),
        source="thispersondoesnotexist",
        hosting="local",
        last_served=datetime.utcnow()
    )

    db.session.add(image_record)
    db.session.commit()
    return


agender = PyAgender()
starttime = time.time()

for a in range(1, times_to_run):
    download_face()
    gender, age = recoginise_face()
    if gender != "unclear":
        print(str(age) + " year old " + gender)
        filename = move_file(gender, age)
        write_db (gender, age, filename)
    else:
        print("gender unclear, so skipping")
    sleep(seconds_to_sleep)

