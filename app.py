from flask import Flask, render_template, request, jsonify, send_from_directory
import base64
import google.generativeai as genai
import os

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
        
        # Process the raw data to extract individual items
        # Split the raw data into individual items based on each fruit
        items = []
        current_item = []
        
        # Split by lines and group them by fruit
        lines = raw_data_string.split('\n')
        for line in lines:
            if line.startswith("Name of fruit:"):
                if current_item:  # If we have collected data for a fruit, add it to items
                    items.append('\n'.join(current_item))
                    current_item = []
                current_item.append(line)
            elif line.strip() and current_item:  # If not empty and we're collecting data
                current_item.append(line)
                
        # Add the last item if there is one
        if current_item:
            items.append('\n'.join(current_item))
            
        raw_inventory_data = items
        
        return jsonify({"success": True, "message": "Inventory updated successfully"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_inventory", methods=["GET"])
def get_inventory():
    return jsonify({"items": raw_inventory_data})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

IMAGE_PATH = "food.jpg"  # Path to your food reference image
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
    
    # ✅ Prepare prompt with raw ESP inventory
    esp_data_string = "\n\n".join(raw_inventory_data)
    
    try:
        # Check if image exists before trying to open it
        if os.path.exists(IMAGE_PATH):
            with open(IMAGE_PATH, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            
            prompt = (
                f"I have the following inventory sent from an ESP32 device with fruits/vegetables in raw format.\n"
                f"Each item contains name, count, freshness %, and estimated rotting days.\n\n"
                f"{esp_data_string}\n\n"
                f"Suggest 5 {category} cuisine dishes that can be made quickly using these items, focusing more on items that may rot sooner. Provide only dish names and short descriptions."
            )
            
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
        else:
            # Fallback if image doesn't exist
            prompt = (
                f"I have the following inventory of fruits/vegetables:\n\n"
                f"{esp_data_string}\n\n"
                f"Suggest 5 {category} cuisine dishes that can be made quickly using these items, focusing more on items that may rot sooner. Provide only dish names and short descriptions.Don't give with text decor."
            )
            
            response = model.generate_content(prompt)
        
        if response and response.text:
            # Process the response to get dish names
            dishes = [dish.strip() for dish in response.text.strip().split("\n") if dish.strip()]
            
            # Limit to 10 dishes maximum
            dishes = dishes[:10]
            
            return jsonify({"success": True, "dishes": dishes})
        else:
            return jsonify({"success": False, "error": "❌ No response from Gemini API"}), 500
    
    except Exception as e:
        app.logger.error(f"Gemini API error: {e}")
        return jsonify({"success": False, "error": f"❌ Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
