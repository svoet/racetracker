FROM python:3.7-alpine
MAINTAINER Symen Voet<symen@rsyc.be>

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

RUN python ./initdb_test.py 

EXPOSE 5000
CMD ["python","./main.py"]
