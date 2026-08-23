FROM python:3.11-slim
WORKDIR /app
COPY whatsapp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY whatsapp ./whatsapp
COPY documents ./documents
CMD ["uvicorn", "whatsapp.app:app", "--host", "0.0.0.0", "--port", "8001"]
