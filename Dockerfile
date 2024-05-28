# Pull the image from Dockerhub
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    && apt-get clean

WORKDIR /outfit_recommendation

# set up python environment variables

ENV PYTHONDOWNWRITEBYTECODE 1
ENV PYTHONNUNBUFFER 1

# update and  install dependencies
COPY ./requirements.txt /api/requirements.txt
RUN pip install -r /api/requirements.txt

# copy project
COPY . .

# Expose the port server is running on
EXPOSE 8000
