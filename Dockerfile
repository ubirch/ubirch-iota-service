FROM python:3.6

WORKDIR /iota-service/
COPY requirements.txt ubirch-iota-service/iotaService.py /iota-service/

RUN pip install -r requirements.txt

CMD ["python", "iotaService.py", "--server='SQS'"]