# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY . ./

# Unpack bert model
COPY bert_model.zip* /tmp/
RUN zip -FF /tmp/bert_model.zip --out /tmp/bert_full.zip && \
    unzip /tmp/bert_full.zip -d /

# Unpack t5 model
COPY t5_decorator_model.zip* /tmp/
RUN zip -FF /tmp/t5_decorator_model.zip --out /tmp/t5_full.zip && \
    unzip /tmp/t5_full.zip -d /

# Install dependencies
COPY requirements_docker.txt ./requirements.txt
RUN chmod +x ./build_backend.sh && \
    ./build_backend.sh && \
    python -m spacy download ro_core_news_sm

# Rename checkpoint
RUN mv /dumitrescustefan_token_output/checkpoint-200-small /dumitrescustefan_token_output/checkpoint-200

EXPOSE 8000
CMD ["python", "main.py"]