FROM python:3.6

WORKDIR /iota-service/

COPY requirements.txt ubirch-iota-service/iota_service.py /iota-service/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "iota_service.py"]
