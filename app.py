import os
import cv2
from mtcnn import MTCNN
from flask import Flask, request, send_file, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return 'No selected file'
        if file:
            # Save the uploaded file
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            # Load the uploaded image
            image = cv2.imread(file_path)
            # Initialize MTCNN for face detection
            detector = MTCNN()
            # Detect faces in the image
            faces = detector.detect_faces(image)
            # Apply blur to each detected face
            for face in faces:
                x, y, w, h = face['box']
                # Extract the region of interest (face)
                face_image = image[y:y+h, x:x+w]
                # Apply a Gaussian blur to the face region
                blurred_face = cv2.GaussianBlur(face_image, (23, 23), 30)
                # Replace the original face region with the blurred one
                image[y:y+h, x:x+w] = blurred_face
            # Save the modified image with blurred faces
            blurred_file_path = os.path.join('uploads', 'blurred_' + file.filename)
            cv2.imwrite(blurred_file_path, image)
            # Return the blurred image file to the user
            return send_file(blurred_file_path, mimetype='image/jpeg', as_attachment=True)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
