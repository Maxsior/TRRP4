import cv2
import requests
from flask import Flask, request
from mimetypes import guess_type
from importlib import import_module
from time import time_ns
import os
import faces_pb2
import base64

app = Flask(__name__)


def deserialize(message, typ):
    module_, class_ = typ.rsplit('.', 1)
    class_ = getattr(import_module(module_), class_)
    rv = class_()
    rv.ParseFromString(message)
    return rv


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
    with open(fname, 'rb') as image:
        img = image.read()
        img = bytes(img)

        for (x, y, w, h) in detect_faces(fname):
            p1 = faces_pb2.Point(x=x, y=y)
            p2 = faces_pb2.Point(x=x+w, y=y+h)
            req = faces_pb2.Crop(image=img, topLeft=p1, bottomRight=p2)
            req = req.SerializeToString()

            response = requests.post(os.getenv('TRRP4_CROP_ADDR'), data=req)

            face = deserialize(response.content, 'faces_pb2.Answer')
            faces.append(base64.b64encode(face.image).decode('ascii'))

    os.remove(fname)

    return {'faces': faces}


def detect_faces(fname):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    return faces


if __name__ == '__main__':
    app.run(debug=True)