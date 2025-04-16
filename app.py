from flask import Flask, render_template, request, jsonify
import base64
import google.generativeai as genai

app = Flask(__name__)

# ✅ Store inventory dynamically with rotting days
inventory_data = {"fruits": {}, "vegetables": {}}

@app.route("/update_inventory", methods=["POST"])
def update_inventory():
    global inventory_data
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # ✅ Store data with optional "estimated_rotting_days"
        inventory_data = data
        return jsonify({"success": True, "message": "Inventory updated successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory_data)

# ✅ Static Image for visual context
IMAGE_PATH = "food.jpg"
GEMINI_API_KEY = "AIzaSyBCWOXDVefsY7f8Q1d9N1HN3Mo6RA1b5eU"  # Replace with your actual key

# ✅ Gemini model setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_dishes", methods=["POST"])
def generate_dishes():
    global inventory_data
    data = request.get_json()
    category = data.get("category")

    if not category:
        return jsonify({"success": False, "error": "❌ No category provided"}), 400

    # ✅ Extract fresh ingredients with optional rotting days info
    available_ingredients = []
    rotting_info = []
    for cat_name, items in inventory_data.items():
        for item, freshness_info in items.items():
            if not isinstance(freshness_info, dict):
                continue

            fresh_count = freshness_info.get("freshness above 80%", 0)
            if fresh_count > 0:
                available_ingredients.append(item)

                # Optional: capture rotting estimate if provided
                days = freshness_info.get("estimated_rotting_days")
                if days is not None:
                    rotting_info.append(f"{item} (rots in {days} days)")
                else:
                    rotting_info.append(f"{item}")

    if not available_ingredients:
        return jsonify({"success": False, "error": "❌ No fresh ingredients available"}), 400

    # ✅ Encode image as base64
    with open(IMAGE_PATH, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # ✅ Gemini prompt with rotting estimates included
    prompt = (
        f"I have the following fresh ingredients with estimated time before rotting:\n"
        f"{', '.join(rotting_info)}.\n"
        f"Suggest 10 {category} cuisine dishes that can be made quickly using these ingredients. "
        f"Focus on using items that may rot sooner. Provide only dish names and short descriptions."
    )

    try:
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])

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
