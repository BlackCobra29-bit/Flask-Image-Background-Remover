from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from rembg import remove
from PIL import Image
import os

app = Flask(__name__)

# Define folders for uploads and processed images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROCESSED_FOLDER = os.path.join('static', 'processed')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Get the image names from the URL parameters, if available
    original_image = request.args.get('original_image')
    processed_image = request.args.get('processed_image')
    return render_template('index.html', original_image=original_image, processed_image=processed_image)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'image' not in request.files:
        return "No file part in the request", 400

    file = request.files['image']
    if file.filename == '':
        return "No file selected", 400

    if file:
        # Save the original image to the uploads folder
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(original_path)

        # Process the image to remove background
        image = Image.open(original_path)
        output = remove(image)

        # Convert the image to RGB before saving as JPEG (if the mode is RGBA)
        if output.mode == 'RGBA':
            output = output.convert('RGB')

        # Save the processed image to the processed folder
        processed_filename = f"processed_{file.filename.rsplit('.', 1)[0]}.jpg"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        output.save(processed_path, 'JPEG')

        # Redirect to display the original and processed images
        return redirect(url_for('index', original_image=file.filename, processed_image=processed_filename))

@app.route('/download/<filename>')
def download_file(filename):
    # Send the processed image for download
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
