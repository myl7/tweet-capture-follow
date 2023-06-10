FROM python:3.11-alpine

RUN apk add --no-cache chromium chromium-chromedriver

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt \
  && mkdir /data

ENV CAPTURE_DIR=/data CHROMEDRIVER_PATH=/usr/bin/chromedriver

VOLUME [ "/data" ]

COPY main.py /app/

ENTRYPOINT ["python", "/app/main.py"]
