import cv2
import requests
import flask
import time
import json
import asyncio
import socket
from multiprocessing import Process, Queue
import threading
from flask import Flask, render_template, Response, jsonify
from azure.iot.device.aio import IoTHubModuleClient

app = Flask(__name__)

def flask_run(frame_queue):
    app.run(host='0.0.0.0', port="5000")

@app.route('/')
def index():
    return render_template('index.html',)

def gen():
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_queue.get() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                mimetype='multipart/x-mixed-replace; boundary=frame')

async def camera(frame_queue):
    headers = {'Content-Type': 'application/octet-stream'}

    # get ip adedress of other container
    tensorflow_container_ip=socket.gethostbyname('model_module')
    tensorflow_container_ip='http://'+tensorflow_container_ip+':80'+'/image'

    # get camera frame
    cap = cv2.VideoCapture(0)
    
    module_client = IoTHubModuleClient.create_from_edge_environment()
    
    await module_client.connect()

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        height, width, channels = frame.shape

        ret, encodedFrame=cv2.imencode(".jpg",frame)

        try:
            response = requests.post(url=tensorflow_container_ip, headers = headers, data = encodedFrame.tostring())
            response_json = response.json()
            response_json = response_json["predictions"]

            json_output={}
            for box in response_json:
                if float(box["probability"]) > 0.6:
                    x1=int(float(box["boundingBox"]["left"])*width)
                    y1=int(float(box["boundingBox"]["top"])*height)
                    x2=int(x1+float(box["boundingBox"]["width"])*width)
                    y2=int(y1+float(box["boundingBox"]["height"])*height)
                    
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
                    text=box["tagName"]+' '+str(round(box["probability"],2))
                    cv2.putText(frame,text,(x2,y2),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                    
                    json_output[box["tagName"]]=box["probability"]
            
            ret, encodedFrame2=cv2.imencode(".jpg",frame)
            frame_byte=encodedFrame2.tobytes()
            
            if int(frame_queue.qsize()) > 2:
                frame_queue.get()
                frame_queue.put(frame_byte)
            else:
                frame_queue.put(frame_byte)
            
            if len(json_output) != 0:
                await module_client.send_message_to_output(json.dumps(json_output), "output")
            
            json_output={}

        except:
            await module_client.send_message_to_output('something wrong from camera code', "output")
            time.sleep(2)

if __name__ == '__main__':
    frame_queue=Queue()

    camera_process = Process(target=flask_run, args=(frame_queue,))
    camera_process.start()

    asyncio.run(camera(frame_queue))