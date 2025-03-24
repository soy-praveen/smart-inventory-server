from flask import Flask, render_template, request, jsonify
import os
import subprocess
import requests

app = Flask(__name__)

# ✅ Path where the uploaded image will be stored
STATIC_FOLDER = "static"
IMAGE_PATH = os.path.join(STATIC_FOLDER, "food.jpg")

# ✅ Ensure static folder exists
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ✅ Your local PC's Flask server running client.py
CLIENT_URL = "http://172.20.180.218:5001/trigger_upload"
@app.route("/")
def index():
    return render_template("index.html")

# ✅ API Endpoint to receive & replace the image
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return "❌ No file found", 400

    file = request.files["file"]

    if file.filename == "":
        return "❌ No selected file", 400

    try:
        # ✅ Delete old image if exists
        if os.path.exists(IMAGE_PATH):
            os.remove(IMAGE_PATH)
            print("🗑️ Old food.jpg deleted!")

        # ✅ Save new image
        file.save(IMAGE_PATH)
        print(f"✅ New image saved at {IMAGE_PATH}")

        # ✅ Push to GitHub (OPTIONAL)
        push_to_github()

        return "✅ Image uploaded & updated on GitHub!", 200

    except Exception as e:
        return f"❌ Error saving image: {e}", 500

# ✅ Function to push new food.jpg to GitHub
def push_to_github():
    try:
        repo_path = os.getcwd()  # Assuming this script runs in the Git repo
        subprocess.run(["git", "add", IMAGE_PATH], cwd=repo_path)
        subprocess.run(["git", "commit", "-m", "Updated food.jpg"], cwd=repo_path)
        subprocess.run(["git", "push"], cwd=repo_path)
        print("✅ Image pushed to GitHub!")
    except Exception as e:
        print(f"❌ GitHub push failed: {e}")

# ✅ API Endpoint to trigger client.py on the local machine
@app.route("/trigger_client", methods=["POST"])
def trigger_client():
    try:
        # ✅ Send a request to client.py running on the local machine
        response = requests.post(CLIENT_URL)

        if response.status_code == 200:
            return jsonify({"success": True, "message": "✅ client.py triggered successfully!"})
        else:
            return jsonify({"success": False, "error": f"Response {response.status_code}: {response.text}"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"❌ Failed to trigger client.py: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
