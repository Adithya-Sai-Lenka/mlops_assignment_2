import socket
import spacy
import os
import httpx
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from gtts import gTTS
import io
import base64

load_dotenv()

app = Flask(__name__)

# Load spaCy model (English small model)
# Must run the download command (see below) for this to work.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Error: Model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

@app.route('/ner', methods=['POST'])
def ner_endpoint():
    """
    Developer B: Named Entity Recognition
    Extracts entities (like names, dates, organizations) from text.
    """
    # 1. Input Validation
    if not nlp:
        return jsonify({"error": "spaCy model not loaded on server."}), 500
        
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid input. Please provide a 'text' field."}), 400

    text = data['text']

    # 2. Process Text
    doc = nlp(text)
    
    # 3. Extract Entities
    # We return the text of the entity and its label (e.g., "Apple", "ORG")
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    return jsonify({
        "entities": entities,
        "service": "ner-worker",
        "container_id": socket.gethostname()
    })

DEEPL_API_URL = "https://api-free.deepl.com/v2/translate" #DeepL Free API

@app.route('/translate', methods=['POST'])
def translate_text():
    """
    Developer A: Text Translation
    Translate text using Google Cloud Translation API.
    """

    api_key = os.getenv("DEEPL_API_KEY")
    if not api_key:
        return jsonify({"error": "DEEPL_API_KEY environment variable not set"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    text = data.get("text","").strip()

    target_language = data.get("target_language", "").strip().upper()
    source_language = data.get("source_language", "").strip().upper()

    if not text:
        return jsonify({"error": "Field 'text' is required"}), 400
    if not target_language:
        return jsonify({"error": "Field 'target_language' is required (e.g. 'FR', 'ES', 'DE')"}), 400
    
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}"
    }

    payload = {
        "text": [text],  
        "target_lang": target_language
    }

    if source_language:
        payload["source_lang"] = source_language

    try:
        response = httpx.post(DEEPL_API_URL, headers=headers, data=payload, timeout=10.0)
        response.raise_for_status()
        
        result_json = response.json()
        translated_item = result_json["translations"][0]
        translated_text = translated_item["text"]
        
        # If source wasn't provided, use the detected one for the response
        detected_source = translated_item.get("detected_source_language", "UNKNOWN")
        final_source = source_language if source_language else detected_source

        return jsonify({
            "original_text":   text,
            "translated_text": translated_text,
            "source_language": final_source,
            "target_language": target_language,
            "container_id":    socket.gethostname()
        }), 200
    
    except httpx.HTTPStatusError as e:
        # Attempt to parse DeepL specific error messages
        try:
            msg = e.response.json().get("message", str(e))
        except Exception:
            msg = str(e)
        return jsonify({"error": msg}), e.response.status_code
    
    except httpx.RequestError as e:
        return jsonify({"error": f"Translation API unreachable: {str(e)}"}), 503

    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response from Translation API"}), 502
    
    
FAL_API_URL       = "https://fal.run/fal-ai/flux/schnell"
VALID_IMAGE_SIZES = [
    "square", "square_hd",
    "landscape_4_3", "landscape_16_9",
    "portrait_4_3",  "portrait_16_9"
]

@app.route('/image-generate', methods=['POST'])
def generate_image():
    """
    Developer A: Image Generation
    Generate images based on text prompts using FAL AI.
    """
    api_key = os.getenv("FALAI_API_KEY")
    
    if not api_key:
        return jsonify({"error": "FALAI_API_KEY environment variable not set"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    prompt = data.get("prompt", "").strip()
    image_size = data.get("image_size", "landscape_4_3") #can change to anything in VALID_IMAGE_SIZES
    num_steps  = data.get("num_inference_steps", 4)

    if not prompt:
        return jsonify({"error": "Field 'prompt' is required"}), 400
    if len(prompt) > 1000:
        return jsonify({"error": "Prompt exceeds 1000 character limit"}), 400
    if image_size not in VALID_IMAGE_SIZES:
        return jsonify({"error": f"Invalid 'image_size'. Valid options: {VALID_IMAGE_SIZES}"}), 400
    if not isinstance(num_steps, int) or not (1 <= num_steps <= 12):
        return jsonify({"error": "num_inference_steps must be an integer between 1 and 12"}), 400

    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type":  "application/json"
    }
    payload = {
        "prompt":                prompt,
        "image_size":            image_size,
        "num_inference_steps":   num_steps,
        "num_images":            1,
        "enable_safety_checker": True
    }

    try:
        response = httpx.post(FAL_API_URL, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        image_url = response.json()["images"][0]["url"]

        return jsonify({
            "prompt":       prompt,
            "image_url":    image_url,
            "image_size":   image_size,
            "container_id": socket.gethostname()
        }), 200

    except httpx.HTTPStatusError as e:
        try:
            msg = e.response.json().get("message", str(e))
        except Exception:
            msg = str(e)
        return jsonify({"error": msg}), e.response.status_code
    
    except httpx.RequestError as e:
        return jsonify({"error": f"Image Generation API unreachable: {str(e)}"}), 503
    
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response from Image Generation API"}), 502
    

@app.route('/speech', methods=['POST'])
def speech_endpoint():
    """
    Developer B: Speech Synthesis using Google Translate TTS (gTTS)
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
        
    text = data['text']
    
    try:
        # 1. Generate Speech in Memory (No API Key needed)
        tts = gTTS(text=text, lang='en')
        
        # 2. Save to a bytes buffer instead of a file
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # 3. Encode to Base64
        audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
        
        return jsonify({
            "audio_base64": audio_base64,
            "service": "speech-worker",
            "model": "google-gtts",
            "container_id": socket.gethostname()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)