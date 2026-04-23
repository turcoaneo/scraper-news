# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

COPY requirements_docker.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -f https://download.pytorch.org/whl/cpu

COPY . ./

CMD ["python", "main.py"]
