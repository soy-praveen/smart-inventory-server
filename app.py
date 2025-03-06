from flask import Flask, render_template, request
import os

app = Flask(__name__)

# ✅ Set up paths
STATIC_FOLDER = "static"
IMAGE_PATH = os.path.join(STATIC_FOLDER, "food.jpg")

# ✅ Ensure static folder exists
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

# ✅ API Endpoint to receive & save the uploaded image
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return "❌ No file found", 400

    file = request.files["file"]
    
    if file.filename == "":
        return "❌ No selected file", 400

    try:
        file.save(IMAGE_PATH)  # Save image to static folder
        print(f"✅ Image saved to {IMAGE_PATH}")
        return "✅ Image uploaded successfully", 200
    except Exception as e:
        return f"❌ Error saving image: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
