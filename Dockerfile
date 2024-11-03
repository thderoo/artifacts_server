FROM python:3.12-slim

WORKDIR /opt/artifacts_server/

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "src/main.py" ]