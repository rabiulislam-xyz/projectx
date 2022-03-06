FROM python:3.9.6-slim

ENV PYTHONUNBUFFERED 1
ENV PORT 8000

WORKDIR /app

RUN apt-get update && apt-get install build-essential -y

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8000
