import json
from flask import request, render_template, jsonify, send_file, Blueprint
import os
import shutil
from werkzeug.utils import secure_filename
from app.utils.email_extraction import process_emails,getDupliactes,resetDupliactes
from app import app

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/upload", methods=["POST"])
def upload():
    """Handles file uploads."""
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    shutil.rmtree(app.config["UPLOAD_FOLDER"])  # Clean previous files
    os.makedirs(app.config["UPLOAD_FOLDER"])
    resetDupliactes()
    
    for file in request.files.getlist("files"):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    process_emails(app.config["UPLOAD_FOLDER"], app.config)
    return jsonify({"message": "Processing complete!"})

# @bp.route("/download")
# def download():
#     return send_file(app.config["OUTPUT_FILE"], as_attachment=True)

# @bp.route('/view_output')
# def view_output():
#     data = load_json()
#     return render_template('output.html', data=data)

def load_json():
    with open(app.config["OUTPUT_FILE"], "r") as file:
        return json.load(file)
    
@bp.route("/view_output")
def view_output():
    return render_template("output.html")

@bp.route("/get_json_data")
def get_json_data():
    processed_data = load_json()
    return jsonify(processed_data)

@bp.route("/get_duplicate_data")
def get_duplicate_data():
    return getDupliactes()


@app.route("/download")
def download():
    output_file = "processed_results.json"
    processed_data = load_json()
    # Save processed data to a file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=4)
    
    return send_file(output_file, as_attachment=True, mimetype="application/json", download_name="processed_results.json")
    

def init_app(app):
    app.register_blueprint(bp)