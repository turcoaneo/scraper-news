# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY . ./

COPY requirements_docker.txt ./requirements.txt

RUN python -m pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "main.py"]