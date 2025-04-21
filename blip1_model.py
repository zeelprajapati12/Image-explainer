from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model & processor
def load_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    return processor, model

processor, model = load_model()

# Main explain function
def explain_image(image_path, prompt=None):
    image = Image.open(image_path).convert("RGB")

    if not prompt or prompt.strip() == "":
        prompt = (
            "Describe the image in detail including objects, actions, background, emotions, and context. "
            "Write it as a single paragraph."
        )

    # Encode only the image — BLIP1 is a vision-to-text model, it does not require a text prompt in the input
    inputs = processor(image, return_tensors="pt").to(device)

    output = model.generate(
        **inputs,
        max_new_tokens=250,
        num_beams=5,
        temperature=0.6,
        top_k=80,
        top_p=0.95,
        repetition_penalty=0.6
    )

    caption = processor.decode(output[0], skip_special_tokens=True)
    
    return caption
