FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install "unstructured[all-docs]"

COPY ./app /app