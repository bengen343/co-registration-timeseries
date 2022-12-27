# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY config.py main.py load_timeseries.py save_to_bq.py ./

CMD [ "python3", "./main.py" ]
