from flask import Flask, render_template, request, jsonify
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model and processor once at startup
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

@app.route("/image_explainer", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/explain", methods=["POST"])
def explain():
    file = request.files.get("image")
    user_prompt = request.form.get("prompt", "").strip()

    if not file or not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return jsonify({"error": "Please upload a valid JPG, JPEG, or PNG image."})

    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    try:
        raw_image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"})

    # Do not send the prompt to the model (BLIP-1 doesn't require it)
    inputs = processor(raw_image, return_tensors="pt").to(device)

    output = model.generate(
    **inputs,
    max_new_tokens=100,           # Reduce tokens to limit rambling
    num_beams=4,                  # Slightly reduce beam count for speed
    temperature=0.7,              # Lower temp = more focused
    top_k=40,                     # Tighter vocab control
    top_p=0.9,                    # Slightly more filtering
    repetition_penalty=1.3        # Stronger anti-repetition
)


    caption = processor.decode(output[0], skip_special_tokens=True)

    # Include user prompt back in response if you want to show it
    return jsonify({
        "result": caption,
        "used_prompt": user_prompt or "[No user prompt provided — used default behavior]"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
