from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess

app = Flask(__name__)

# ✅ Path where the uploaded image will be stored
IMAGE_PATH = "food.jpg"  # Ensure food.jpg is in the same folder as app.py

@app.route("/")
def index():
    return render_template("index.html")

# ✅ Trigger client.py to upload image
@app.route("/trigger_client", methods=["POST"])
def trigger_client():
    try:
        subprocess.run(["python", "client.py"], check=True)
        return jsonify({"success": True, "message": "✅ client.py executed successfully!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e)})

# ✅ Serve the latest uploaded image
@app.route("/get_image")
def get_image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype="image/jpeg")
    return "❌ No image found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
