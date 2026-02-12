
import os
from flask import Flask, request, jsonify
from PIL import Image
from ai_logic import AIModule

app = Flask(__name__)

# Initialize AI Module lazy, or global if API key is present
ai_module = None

def get_ai_module():
    global ai_module
    if ai_module is None:
        try:
            ai_module = AIModule()
        except Exception as e:
            print(f"Error initializing AI module: {e}")
            raise e
    return ai_module

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "SENP_AI_Backend"}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        module = get_ai_module()
    except Exception as e:
        return jsonify({"error": f"Failed to initialize AI: {str(e)}"}), 500

    if 'image' not in request.files and 'images' not in request.files:
         return jsonify({"error": "No image provided"}), 400
    
    user_question = request.form.get('question', '')
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    images = []
    try:
        # Handle multiple images (e.g. for scrolling captures)
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                img = Image.open(file.stream)
                images.append(img)
        # Handle single image
        elif 'image' in request.files:
            file = request.files['image']
            img = Image.open(file.stream)
            images.append(img)
            
        result = module.analyze_images(images, user_question)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

if __name__ == "__main__":
    # Cloud Run expects the app to listen on PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
