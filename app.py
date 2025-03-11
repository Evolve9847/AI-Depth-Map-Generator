from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import time
from werkzeug.utils import secure_filename
from depth_estimation import estimate_depth, save_depth_map

# Initialize Flask
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("file")  # Support multiple files
    output_format = request.form.get('format', 'png')

    if not files or not all(allowed_file(file.filename) for file in files):
        return jsonify({"error": "Invalid file format. Only PNG and JPEG are allowed."}), 400

    output_images = []
    start_time = time.time()

    for file in files:
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        output_filename = os.path.splitext(filename)[0] + f".{output_format}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        print(f"📂 Processing: {filename}")
        depth_map = estimate_depth(input_path)

        save_depth_map(depth_map, output_path)
        output_images.append(output_filename)

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)

    return render_template(
        'index.html',
        output_images=output_images,
        processing_time=processing_time
    )


@app.route('/static/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
