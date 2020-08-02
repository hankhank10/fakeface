import requests
import shutil
import cv2
import secrets
from pyagender import PyAgender
import time

from time import sleep

# settings
url = "https://thispersondoesnotexist.com/image"
male_threshold = 0.4
female_threshold = 0.6
temp_file = "temp_img.jpg"
seconds_to_sleep = 1


def download_face():
    response = requests.get(url, stream=True)
    with open(temp_file, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return

def recoginise_face():
    faces = agender.detect_genders_ages(cv2.imread(temp_file))
    face = faces[0]
    gender_numeric = face['gender']
    age = int(face['age'])

    gender = "unclear"
    if gender_numeric < male_threshold: gender = "male"
    if gender_numeric > male_threshold: gender = "female"

    return gender, age

def move_file(gender, age):
    category = "older"
    if age < 50: category = "adult"
    if age < 30: category = "young_adult"
    if age < 20: category = "child"

    if category == "older":
        location_to_move_to = gender + "/" + gender + "/" + category + "/" + gender + "_" + str(age) + "_" + secrets.token_hex(10) + ".jpg"
        shutil.move(temp_file, location_to_move_to)
    else:
        print ("Wrong category, so skipping save")
    return


agender = PyAgender()
starttime = time.time()

print("Getting " + str(times_to_run) + " faces")
for a in range(1, times_to_run):
    print("Downloading face " + str(a) + " of " + str(times_to_run) + "... ", end='')
    download_face()
    gender, age = recoginise_face()
    if gender != "unclear":
        print(str(age) + " year old " + gender)
        move_file(gender, age)
    else:
        print("gender unclear, so skipping")
    sleep(seconds_to_sleep)

print("Done in", time.time() - starttime, "seconds")
