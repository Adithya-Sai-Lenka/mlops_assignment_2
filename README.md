[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/R5VR2ocT)

# DA5402 Assignment 2 — Multi-Modal AI REST API

**Team:** Khushi Gatwar (DA25S004) — Developer A | Adithya Sai Lenka (DA25S008) — Developer B

**Repository:** [assignment-2-da25s004-da25s008](https://github.com/DA5402-MLOps-JAN26/assignment-2-da25s004-da25s008)

---

## 📖 Project Overview
A Flask-based REST API providing four AI-powered endpoints across two developers, built with a Git branching workflow and documented merge conflict resolution.

### Endpoints
| Method | Endpoint | Developer | Technology |
|---|---|---|---|
| POST | `/translate` | A | DeepL Translation API |
| POST | `/image-generate` | A | fal.ai FLUX Schnell |
| POST | `/ner` | B | spaCy (en_core_web_sm) |
| POST | `/speech` | B | Google TTS (gTTS) |

---

## 🚀 Quick Start & Installation

### 1. Clone and Install
```bash
git clone https://github.com/DA5402-MLOps-JAN26/assignment-2-da25s004-da25s008.git
cd assignment-2-da25s004-da25s008

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Model Assets (Required for NER)
The Named Entity Recognition service requires the English language model from spaCy:

```bash
python -m spacy download en_core_web_sm
```

### 3. Configure API Keys
Create a `.env` file in the root directory:

```bash
DEEPL_API_KEY=your_deepl_api_key_here
FALAI_API_KEY=your_fal_api_key_here
```

**Get your API keys:**
- **DeepL:** [deepl.com/pro-api](https://www.deepl.com/pro-api) → Free tier: 500,000 chars/month
- **fal.ai:** [fal.ai](https://fal.ai) → Free tier: $1 credit on signup

### 4. Run the Server
```bash
python app.py
```
Server starts at `http://localhost:8000`

---

## API Documentation

🟢 Developer A Services (Translation & Image)

#### 1. Translate (/translate)
Translate text between languages using DeepL.
Request:
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "FR",
    "source_language": "EN"
  }'
```
Response:
```JSON
{
  "container_id": "macbook-pro.local",
  "original_text": "Hello, how are you?",
  "source_language": "EN",
  "target_language": "FR",
  "translated_text": "Bonjour, comment allez-vous ?"
}
```

#### 2. Image Generation (/image-generate)
Generate AI images from text prompts using fal.ai FLUX Schnell.
Request:
```bash
curl -X POST http://localhost:8000/image-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic cyberpunk city at sunset with neon lights",
    "image_size": "landscape_4_3",
    "num_inference_steps": 4
  }'
```
Response:
```JSON
{
  "prompt": "A futuristic cyberpunk city at sunset...",
  "image_url": "[https://fal.media/files/](https://fal.media/files/)...",
  "image_size": "landscape_4_3",
  "container_id": "macbook-pro.local"
}
```

🔵 Developer B Services (NER & Speech)

#### 3. Named Entity Recognition (/ner)
Identifies and classifies named entities (Person, Org, GPE, etc.) in the input text using spaCy.
Request:
```bash
curl -X POST http://localhost:8000/ner \
     -H "Content-Type: application/json" \
     -d '{"text": "Sundar Pichai is hiring for Google in Bangalore."}'
```
Response:
```JSON
{
  "entities": [
    { "label": "PERSON", "text": "Sundar Pichai" },
    { "label": "ORG", "text": "Google" },
    { "label": "GPE", "text": "Bangalore" }
  ],
  "service": "ner-worker"
}
```

#### 4. Speech Synthesis (/speech)
Generates spoken audio from text using gTTS. Returns a Base64-encoded MP3 string.
Request:
```JSON
{
  "text": "Hello, this is a test of the speech endpoint."
}
```
Testing Guide (Save to MP3):
Run this command to decode the Base64 response and save it as an audio file:
```bash
curl -s -X POST http://localhost:8000/speech \
-H "Content-Type: application/json" \
-d '{"text": "Hello, this is a test of the speech endpoint."}' \
| python3 -c "import sys, json, base64; open('output.mp3', 'wb').write(base64.b64decode(json.load(sys.stdin)['audio_base64']))"
```
Expected Output: An `output.mp3` file will be created in your directory.
