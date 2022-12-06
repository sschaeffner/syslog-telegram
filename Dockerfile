# syntax=docker/dockerfile:1

FROM python:3.9.15-slim
WORKDIR /app
COPY sysloghandler.py requirements.txt /app/
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]