# syntax=docker/dockerfile:1
FROM python:3.11.0-slim

WORKDIR /app

COPY . ./

COPY requirements_docker.txt ./requirements.txt

RUN chmod +x ./build_backend.sh
RUN ./build_backend.sh

CMD ["python", "main.py"]