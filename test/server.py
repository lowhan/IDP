import cv2
import base64
from screeninfo import get_monitors
from flask import Flask
from flask_socketio import SocketIO, emit

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Get the screen resolution of the device
#screen = get_monitors()[0]
#screen_width, screen_height = screen.width, screen.height

device="/dev/video0"
api= cv2.CAP_OPENCV_MJPEG

# OpenCV VideoCapture
cap = cv2.VideoCapture(device)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

def emit_frames():
    while True:
        ret, frame = cap.read()
        if ret:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                # Convert buffer to base64 string
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                # Emit the frame to the client
                socketio.emit("frame", jpg_as_text)

# Start emitting frames when the SocketIO connection is established
@socketio.on('connect')
def on_connect():
    print('Client connected')
    emit('connection_response', 'Connected')
    socketio.start_background_task(emit_frames)

# Release the webcam when the SocketIO connection is closed
@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')
    cap.release()

if __name__ == '__main__':
    socketio.run(app, port=5000, host = "0.0.0.0", debug=False)
