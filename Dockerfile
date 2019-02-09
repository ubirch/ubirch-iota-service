FROM python:3.6

LABEL description="ubirch IOTA anchoring service"


WORKDIR /iota-service/

COPY requirements.txt /iota-service/
RUN pip install -r requirements.txt

COPY ubirch-iota-service/iota_service.py /iota-service/
COPY start.sh /iota-service/
RUN chmod +x ./start.sh


ENV LOGLEVEL="DEBUG"

CMD ["./start.sh"]