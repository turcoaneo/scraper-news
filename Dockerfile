# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY . ./

COPY requirements_docker.txt ./requirements.txt

RUN mv /dumitrescustefan_token_output/checkpoint-200-small /dumitrescustefan_token_output/checkpoint-200

EXPOSE 8000
CMD ["python", "main.py"]