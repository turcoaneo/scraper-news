# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY . ./

COPY requirements_docker.txt ./requirements.txt
RUN mv ./dumitrescustefan_token_output/checkpoint-200-small ./dumitrescustefan_token_output/checkpoint-200

RUN chmod +x ./build_backend.sh
RUN ./build_backend.sh
RUN python -m spacy download ro_core_news_sm

EXPOSE 8000
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "main.py"]