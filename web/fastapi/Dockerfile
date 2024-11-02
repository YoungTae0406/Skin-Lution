FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN pip install --upgrade pip 
RUN apt-get update && apt-get install -y sqlite3 
RUN pip install passlib[bcrypt] python-jose sqlalchemy alembic

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]