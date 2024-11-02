FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY requirements.txt /app

RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1 && apt-get install -y poppler-utils && apt-get install -y tesseract-ocr
RUN python -m nltk.downloader punkt averaged_perceptron_tagger