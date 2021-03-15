FROM python:3.6.12-buster
MAINTAINER Talmaza Viktoria

WORKDIR /usr/src/pythonproxy
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD python proxy.py & python web_interface.py

EXPOSE 8000 8081
