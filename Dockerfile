# syntax=docker/dockerfile:1
FROM pytorch/pytorch:2.2.2-cpu

WORKDIR /app

COPY requirements_docker.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . ./

CMD ["python", "main.py"]
