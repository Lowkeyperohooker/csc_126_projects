from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)

face_detector=cv2.CascadeClassifier('csc_126_projects\project_1\Haarcascades\haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('csc_126_projects\project_1\Haarcascades\haarcascade_eye.xml')

def gen_frames(detect_faces=True, detect_eyes=True):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if detect_faces:
                faces = face_detector.detectMultiScale(gray, 1.1, 7)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    if detect_eyes:
                        roi_gray = gray[y:y+h, x:x+w]
                        roi_color = frame[y:y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                        for (ex, ey, ew, eh) in eyes:
                            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            elif detect_eyes:  
                eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)  
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    detect_faces = request.args.get('faces', 'true').lower() == 'true'
    detect_eyes = request.args.get('eyes', 'true').lower() == 'true'
    return Response(gen_frames(detect_faces, detect_eyes), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
