from flask import Flask
import faces

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/get_face')
def get_face():
    faces.download_face()
    gender, age = faces.recoginise_face()
    return gender


if __name__ == '__main__':
    app.run(debug=true)
