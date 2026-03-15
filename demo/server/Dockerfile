FROM python:3.11-slim

WORKDIR /app

# Copy source agents
COPY ../../src /app/src

# Copy server
COPY . /app/server

WORKDIR /app/server

RUN pip install --no-cache-dir fastapi>=0.110.0 uvicorn>=0.27.0 websockets>=12.0 pymongo>=4.6.0 python-multipart>=0.0.9 loguru>=0.7.0 pyyaml>=6.0

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
