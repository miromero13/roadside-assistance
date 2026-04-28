FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# FastAPI necesita escuchar en el puerto que Google le asigne
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]