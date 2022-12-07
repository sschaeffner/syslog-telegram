# syntax=docker/dockerfile:1

FROM python:3.11.0-slim
WORKDIR /app
COPY sysloghandler.py requirements.txt thegram.py /app/
RUN pip3 install -r requirements.txt
CMD ["python3", "thegram.py"]