FROM python:3.11

WORKDIR /app

RUN pip install cryptography

COPY o.py /app/

CMD ["python3", "o.py"]
