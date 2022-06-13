# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster
WORKDIR /anti-procrastination
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt