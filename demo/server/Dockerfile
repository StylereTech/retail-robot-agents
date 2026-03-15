FROM python:3.11-slim
WORKDIR /app
COPY ../../requirements.txt /app/requirements.txt
RUN pip install fastapi uvicorn websockets pymongo python-multipart loguru pyyaml httpx anthropic openai pydantic python-dotenv rich --no-cache-dir
COPY ../../src /app/src
COPY . /app/demo/server
WORKDIR /app/demo/server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
