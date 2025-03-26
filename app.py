from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# ✅ Store inventory dynamically
inventory_data = {"fruits": {}, "vegetables": {}}

# ✅ API Endpoint to Receive Inventory Updates
@app.route("/update_inventory", methods=["POST"])
def update_inventory():
    global inventory_data
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        inventory_data = data  
        return jsonify({"success": True, "message": "Inventory updated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ✅ API Endpoint to Serve Inventory Data to Frontend
@app.route("/get_inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory_data)

# ✅ Configure Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # 🔥 Load from environment variable

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None  # Handle missing API key

@app.route("/")
def index():
    return render_template("index.html")

# ✅ Generate Dish Suggestions from Gemini AI (without image)
@app.route("/generate_dishes", methods=["POST"])
def generate_dishes():
    global inventory_data
    if not model:
        return jsonify({"success": False, "error": "❌ Gemini API key is missing"}), 500

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

    # ✅ New Prompt for Gemini API
    prompt = (
        f"I have the following fresh ingredients: {', '.join(available_ingredients)}. "
        f"Suggest 10 dishes that can be made using them, focusing on {category} cuisine. "
        f"Provide only dish names and a short description without numbers or special formatting."
    )

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            dishes = response.text.strip().split("\n")
            return jsonify({"success": True, "dishes": dishes})
        else:
            return jsonify({"success": False, "error": "❌ No response from Gemini API"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ✅ Get Render-assigned Port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
