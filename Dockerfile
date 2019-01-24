FROM python:3.6

LABEL description="ubirch IOTA anchoring service"


ARG LOGLEVEL='DEBUG'

ARG IOTA_ADDRESS='9E99GKDY9BYDQ9PGOHHMUWJLBDREMK9BVHUFRHVXCVUIFXLNTZMXRM9TDXJKZDAKIGZIMCJSH9Q9V9GKW'
ARG IOTA_SEED=None
ARG IOTA_NODE_URI='https://nodes.devnet.iota.org:443'
ARG IOTA_DEPTH=6

ARG KAFKA_PORT=['localhost:9092']

ARG SQS_URL="http://localhost:9324"
ARG SQS_REGION="elasticmq"
ARG SQS_SECRET_ACCESS_KEY="x"
ARG SQS_KEY_ID="x"

ENV SERVER=${SERVER}
ENV LOGLEVEL=${LOGLEVEL}

ENV IOTA_ADDRESS=${IOTA_ADDRESS}
ENV IOTA_SEED=${IOTA_SEED}
ENV IOTA_NODE_URI=${IOTA_NODE_URI}
ENV IOTA_DEPTH=${IOTA_DEPTH}

ENV KAFKA_PORT=${KAFKA_PORT}

ENV SQS_URL=${SQS_URL}
ENV SQS_REGION=${SQS_REGION}
ENV SQS_SECRET_ACCESS_KEY=${SQS_SECRET_ACCESS_KEY}
ENV SQS_KEY_ID=${SQS_KEY_ID}

WORKDIR /iota-service/

COPY requirements.txt /iota-service/
RUN pip install -r requirements.txt

COPY ubirch-iota-service/iota_service.py /iota-service/

COPY start.sh /iota-service/
RUN chmod +x ./start.sh

# ENTRYPOINT ["python", "iota_service.py"]
CMD ["./start.sh"]
