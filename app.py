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

UPLOAD_FOLDER = 'C:/Users/SANDEEP/Documents/Python/lab3assignment_reckognition/static/images'

client = boto3.client(
    'rekognition', 
    aws_session_token="FwoGZXIvYXdzEHsaDLWK4/O2HZ+N47fh4yLaAapdUU4emyDo65ZQG0x4ooIYxLn1ull5ONqZrvFT/swMrolBOufkM3F+WWXRqIlbjoP8+9RKXlAVvMm2tuyBX5DxmzrSeMHdZXNTnKyGUAvPURcAzujBeM7nNCr3yzzmg2FTpR6JtqXqBnGYytSMazpD38AI42vW6zPknNO15puSloK/HZRe4I8APixGGxcprU1vbFI2dt1JuhELWKKc0WJacgrfpaVWyQ/C8sIjjc49Am5fZM9PVPR2GFkiVs3FbGk8uG0go/8K47yWLRxUnGI8K73/PayAQ7GaKI673fsFMi3Otf1Rd7rWDLmt7fG+kocnba6jusS2GRVW4sk6zvr/5Yhegyvn1qUVfejakjQ=", 
    aws_secret_access_key="JFrFNXj+XrvZWpefw+pxfyI2gzytn8DQh0W1AORL", 
    aws_access_key_id="ASIASUKMNHTBAI6PBWPJ", 
    region_name='us-east-1'
)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    image = request.files.get('file')
    image.save('image.png')

    file = Image.open(open("image.png",'rb'))
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
    return jsonify(response['FaceDetails'], str(IMG_TAIL) + 'result.png')


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.run(debug=True)