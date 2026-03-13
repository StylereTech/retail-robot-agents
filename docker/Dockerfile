FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ROBOT_SIM_MODE=true
ENV LOG_LEVEL=INFO

CMD ["python", "examples/simple_robot_arm.py"]
