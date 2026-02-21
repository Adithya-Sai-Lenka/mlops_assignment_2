# Dockerfile — DA5402 Assignment 2
# Multi-Modal AI REST API

# LAYER CACHING STRATEGY 

# Docker builds images in layers. Each instruction (FROM, RUN, COPY, etc.) creates a new layer. Layers are cached and reused if nothing has changed.

# Our strategy: ORDER INSTRUCTIONS FROM LEAST TO MOST FREQUENTLY CHANGED

# Layer 1: FROM python:3.11-slim
#   - Cached forever unless we change the base image tag
#   - ~150MB, pulled once and reused across all builds

# Layer 2: RUN apt-get (system dependencies)
#   - Only reruns if we add/remove system packages
#   - Installs gcc/g++ needed for spaCy
#   - Result cached until apt-get command changes

# Layer 3: COPY requirements.txt
#   - Invalidated ONLY when requirements.txt content changes
#   - Docker compares file checksum, not timestamp
#   - If unchanged, all layers below stay cached

# Layer 4: RUN pip install
#   - Only reruns when Layer 3 invalidates (dependencies changed)
#   - Most expensive layer (~200MB, 2-3 minutes on first build)
#   - BUT: if you only change app.py, this layer is SKIPPED entirely

# Layer 5: RUN python -m spacy download
#   - Downloads spaCy English model (~13MB)
#   - Cached unless spacy version changes in requirements.txt

# Layer 6: COPY app.py
#   - Most frequently changed layer (the code)
#   - Invalidates ONLY this layer, everything above stays cached
#   - Result: code changes = 1 second rebuild (just copy app.py)

# WHY THIS MATTERS:
#   Bad order (COPY app.py before requirements.txt):
#     - Every code edit = full pip reinstall = 3 min rebuild
#   Good order (requirements.txt before app.py):
#     - Code edit = 1 sec rebuild (just copy changed file)

# This is the core principle of Docker layer caching optimization.

FROM python:3.11-slim

WORKDIR /app

# Layer 2: System dependencies 
# Install only what's needed: gcc/g++ for compiling spaCy C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Layer 3: Python dependencies (BEFORE app code) 
# Copy requirements.txt FIRST, before app code
# This means code changes don't invalidate the expensive pip install layer
COPY requirements.txt .

# Layer 4: Install Python packages 
RUN pip install --no-cache-dir -r requirements.txt

# Layer 5: Download spaCy language model 
RUN python -m spacy download en_core_web_sm

# Layer 6: Application code (LAST — most frequently changed) 
COPY app.py .

# ── Security: API keys ────────────────────────────────────────────────────────
# API keys are NEVER baked into this image.
# They are injected at runtime via:
#   - docker run -e DEEPL_API_KEY=xxx -e FALAI_API_KEY=yyy
#   - OR via docker-stack.yml environment section

EXPOSE 8000

# Start the Flask server
# debug=False for production (debug mode would restart on code changes)
CMD ["python", "app.py"]
