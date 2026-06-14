FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent/     ./agent/
COPY dashboard/ ./dashboard/
RUN mkdir -p /app/data /app/logs
CMD ["python", "agent/main.py"]