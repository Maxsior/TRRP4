import cv2
from flask import Flask, request
from mimetypes import guess_type
from time import time_ns
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if 'image' not in request.files:
        return 'Wrong parameter name', 400

    image = request.files['image']

    if image.filename == '':
        return 'Empty image', 400

    mime = guess_type(image.filename)[0] or ''
    if not mime.startswith('image'):
        return 'Wrong mime-type'

    ext = image.filename.rpartition('.')[-1]
    fname = f'./{time_ns()}.{ext}'
    image.save(fname)

    faces = []
    for (x, y, w, h) in detect_faces(fname):
        # TODO send faces via protobuf
        faces.append(...)

    os.remove(fname)

    return { 'faces': faces }


def detect_faces(fname):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    return faces


if __name__ == '__main__':
    app.run(debug=True)