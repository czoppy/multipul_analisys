import json
import os
import uuid
from datetime import date
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "papers")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "items.json")
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "epub", "md"}


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(items):
    with open(DATA_FILE, "w") as f:
        json.dump(items, f, indent=2)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/items", methods=["GET"])
def get_items():
    return jsonify(load_data())


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.get_json()
    items = load_data()
    item = {
        "id": str(uuid.uuid4()),
        "title": data.get("title", "").strip(),
        "authors": data.get("authors", "").strip(),
        "year": data.get("year", "").strip(),
        "type": data.get("type", "paper"),
        "status": "todo",
        "link": data.get("link", "").strip(),
        "file": data.get("file", "").strip(),
        "notes": data.get("notes", "").strip(),
        "added": str(date.today()),
    }
    items.append(item)
    save_data(items)
    return jsonify(item), 201


@app.route("/api/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    items = load_data()
    for item in items:
        if item["id"] == item_id:
            for key in ["title", "authors", "year", "type", "status", "link", "file", "notes"]:
                if key in data:
                    item[key] = data[key]
            save_data(items)
            return jsonify(item)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    items = load_data()
    items = [i for i in items if i["id"] != item_id]
    save_data(items)
    return jsonify({"ok": True})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    if f.filename == "" or not allowed_file(f.filename):
        return jsonify({"error": "Invalid file"}), 400
    filename = secure_filename(f.filename)
    f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return jsonify({"filename": filename})


@app.route("/papers/<filename>")
def serve_paper(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("papers", exist_ok=True)
    app.run(debug=True, port=5000)
