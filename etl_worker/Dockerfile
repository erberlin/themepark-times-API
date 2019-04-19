FROM python:3.7.2-alpine

RUN mkdir app

COPY ./data_access ./data_access
RUN pip install -e data_access/.

COPY ./etl_worker ./app/etl_worker

WORKDIR /app/etl_worker

RUN pip install -e .

