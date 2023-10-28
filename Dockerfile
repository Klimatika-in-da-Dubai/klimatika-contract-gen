FROM python:3.11-alpine


RUN apk update \ 
    && apk add --no-cache python3-dev libreoffice msttcorefonts-installer fontconfig openjdk11-jre font-liberation-sans-narrow \
    && update-ms-fonts \
    && fc-cache -f

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD python -m app
