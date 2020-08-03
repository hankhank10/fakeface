from flask import Flask, jsonify, request, redirect

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db.init_app(app)
migrate = Migrate(app, db)


class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)

    filename = db.Column(db.String(100))
    hosting = db.Column(db.String(100), default="local")

    def image_url(self):
        if self.hosting == "local":
            output = "https://fakeface.rest/static/classified/" + self.filename
        return output

    date_added = db.Column(db.DateTime)
    source = db.Column(db.String(100))

    last_served = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.DateTime)
    deleted_at = db.Column(db.Boolean)


@app.route('/')
def hello_world():
    return redirect ("https://docs.fakeface.rest/")


def get_url(gender = "", minimum_age = 0, maximum_age = 0):
    if gender == '':
        db_output = ImageRecord.query.filter(ImageRecord.age >= minimum_age, ImageRecord.age <= maximum_age).order_by(ImageRecord.last_served).first_or_404()

    if gender != '':
        db_output = ImageRecord.query.filter(ImageRecord.gender == gender, ImageRecord.age >= minimum_age, ImageRecord.age <= maximum_age).order_by(ImageRecord.last_served).first_or_404()

    db_output.last_served = datetime.utcnow()
    db.session.commit()
    return db_output.image_url()


@app.route('/face/json')
def output_json():
    gender = request.args.get('gender', '')
    minimum_age = request.args.get('minimum_age', 0)
    maximum_age = request.args.get('maximum_age', 99)

    if gender == '':
        db_output = ImageRecord.query.filter(ImageRecord.age >= minimum_age, ImageRecord.age <= maximum_age).order_by(ImageRecord.last_served).first_or_404()

    if gender != '':
        db_output = ImageRecord.query.filter(ImageRecord.gender == gender, ImageRecord.age >= minimum_age, ImageRecord.age <= maximum_age).order_by(ImageRecord.last_served).first_or_404()

    dict_output = {
        'gender': db_output.gender,
        'age': db_output.age,
        'filename': db_output.filename,
        'date_added': db_output.date_added,
        'source': db_output.source,
        'image_url': db_output.image_url(),
        'last_served': db_output.last_served
    }

    db_output.last_served = datetime.utcnow()
    db.session.commit()

    return jsonify(dict_output)


@app.route ('/face/view')
def output_redirect_image():
    gender = request.args.get('gender', '')
    minimum_age = request.args.get('minimum_age', 0)
    maximum_age = request.args.get('maximum_age', 99)

    url_to_show = get_url(gender, minimum_age, maximum_age)

    return redirect (url_to_show)


@app.route('/stats')
def stats():
    stats_count = ImageRecord.query.count()
    return (str(stats_count) + " faces")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11000, debug=True)
