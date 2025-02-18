from flask import Flask,render_template,Response
import cv2
import os
import serverless_wsgi

app=Flask(__name__)
camera=cv2.VideoCapture(0)

def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

if __name__=="__main__":
    
    # Set the port dynamically (can be used for Heroku or local)
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=PORT, debug=True)



#   "functions": {
#     "app.py": {
#       "runtime": "python@3.9.12"
#     }
#   },