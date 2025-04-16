from flask import Flask, render_template, request, jsonify
import base64
import google.generativeai as genai

app = Flask(__name__)

# ✅ Store raw ESP data
raw_inventory_data = []

@app.route("/update_inventory", methods=["POST"])
def update_inventory():
    global raw_inventory_data
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # ✅ Extract inventory items from the raw string
        raw_data_string = data.get("response", "")
        if not raw_data_string:
            return jsonify({"success": False, "error": "No inventory data provided"}), 400

        # Split the raw data into individual items based on double newlines (\n\n)
        raw_inventory_data = [item.strip() for item in raw_data_string.split("\n\n") if item.strip()]

        return jsonify({"success": True, "message": "Inventory updated successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_inventory", methods=["GET"])
def get_inventory():
    return jsonify({"items": raw_inventory_data})

IMAGE_PATH = "food.jpg"
GEMINI_API_KEY = "AIzaSyBCWOXDVefsY7f8Q1d9N1HN3Mo6RA1b5eU"  # Replace with your actual key

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_dishes", methods=["POST"])
def generate_dishes():
    global raw_inventory_data
    data = request.get_json()
    category = data.get("category")

    if not category:
        return jsonify({"success": False, "error": "❌ No category provided"}), 400

    if not raw_inventory_data:
        return jsonify({"success": False, "error": "❌ No inventory data available"}), 400

    # ✅ Join raw inventory into a prompt
    esp_data_string = "\n\n".join(raw_inventory_data)

    prompt = (
        f"I have the following inventory of fruits and vegetables sent from an ESP32 device.\n"
        f"Each item includes name, quantity, freshness percentage, and estimated rotting days.\n\n"
        f"{esp_data_string}\n\n"
        f"Please suggest 10 {category} cuisine dishes I can prepare quickly using these items, "
        f"prioritizing those that are closer to rotting. Include only the dish names and a short description."
    )

    try:
        response = model.generate_content(prompt)

        if response and response.text:
            dishes = [dish.strip() for dish in response.text.strip().split("\n") if dish.strip()]
            return jsonify({"success": True, "dishes": dishes})
        else:
            return jsonify({"success": False, "error": "❌ No response from Gemini API"}), 500

    except Exception as e:
        app.logger.error(f"Gemini API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
