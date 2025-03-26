from flask import Flask, render_template, request, jsonify, send_file
import os
import socket
import base64
import google.generativeai as genai

app = Flask(__name__)

# ✅ Store inventory dynamically
inventory_data = {"fruits": {}, "vegetables": {}}

# ✅ API Endpoint to Receive Inventory Updates
@app.route("/update_inventory", methods=["POST"])
def update_inventory():
    global inventory_data

    try:
        data = request.json  # Get JSON data from request
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # ✅ Update inventory
        inventory_data = data  
        return jsonify({"success": True, "message": "Inventory updated successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# ✅ API Endpoint to Serve Inventory Data to Frontend
@app.route("/get_inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory_data)

# ✅ Image Path
IMAGE_PATH = "food.jpg"
CLIENT_HOST = "127.0.0.1"
CLIENT_PORT = 5001
GEMINI_API_KEY = "AIzaSyBCWOXDVefsY7f8Q1d9N1HN3Mo6RA1b5eU"  # 🔥 Replace with your actual API key

# ✅ Configure Google Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@app.route("/")
def index():
    return render_template("index.html")


# ✅ Generate Dish Suggestions from Gemini AI
@app.route("/generate_dishes", methods=["POST"])
def generate_dishes():
    global inventory_data
    data = request.json
    category = data.get("category")

    if not category:
        return jsonify({"success": False, "error": "❌ No category provided"}), 400

    # ✅ Extract only "freshness above 80%" items
    available_ingredients = []
    for category_name, items in inventory_data.items():
        for item, freshness_levels in items.items():
            if "freshness above 80%" in freshness_levels and freshness_levels["freshness above 80%"] > 0:
                available_ingredients.append(item)

    if not available_ingredients:
        return jsonify({"success": False, "error": "❌ No fresh ingredients available"}), 400

    # ✅ Convert Image to Base64
    with open(IMAGE_PATH, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # ✅ New Prompt for Gemini API
    prompt = (
        f"I have the following fresh ingredients: {', '.join(available_ingredients)}. "
        f"Suggest 10 dishes that can be made using them, focusing on {category} cuisine. "
        f"Provide only dish names and a short description without numbers or special formatting."
    )

    try:
        # 🔥 Send Prompt & Image to Gemini API
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])

        if response and response.text:
            dishes = response.text.strip().split("\n")  # Extract dish names
            return jsonify({"success": True, "dishes": dishes})
        else:
            return jsonify({"success": False, "error": "❌ No response from Gemini API"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
