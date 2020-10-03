from flask import Flask, render_template, jsonify, request, json, send_file
from PIL import Image, ImageDraw, ExifTags, ImageColor
from flask_cors import CORS
import boto3
import os
import base64
import io
import random



app = Flask(__name__)


CORS(app)

UPLOAD_FOLDER = '/'

client = boto3.client('rekognition')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    image = request.files.get('file')
    image.save('static/images/image.png')

    file = Image.open(open("static/images/image.png",'rb'))
    stream = io.BytesIO()
    file.save(stream, format=file.format)
    image_binary = stream.getvalue()

    response = client.detect_faces(
        Image={
            'Bytes': image_binary
        },
        Attributes=['ALL']
    )

    draw = ImageDraw.Draw(file)

    for faceDetail in response['FaceDetails']:  
        
        imgWidth, imgHeight = file.size

        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)

        )
        draw.line(points, fill='#00d400', width=4)
        
    IMG_TAIL = random.randint(0, 1000000000)
    file.save(os.path.join(UPLOAD_FOLDER, str(IMG_TAIL) + 'result.png'))
    return jsonify(response['FaceDetails'], 'image.png')


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.run(debug=True)