FROM python:3.12-slim

WORKDIR /opt/artifact_server/

COPY requirements.txt $WORKDIR

RUN pip install -r requirements.txt

RUN python ./src/main.py