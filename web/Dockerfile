FROM python:3.7.2-alpine

RUN mkdir app

COPY ./data_access ./data_access
RUN pip install -e data_access/.

COPY ./web ./app/web

WORKDIR /app/web

RUN pip install -r requirements.txt