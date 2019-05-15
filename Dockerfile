FROM python:3.6-alpine

LABEL description="ubirch IOTA anchoring service"

WORKDIR /iota-service/

RUN apk update
RUN apk add build-base libffi-dev openssl-dev

COPY requirements.txt /iota-service/
RUN pip install -r requirements.txt

COPY ubirch-iota-service/iota_service.py /iota-service/
COPY start.sh /iota-service/
RUN chmod +x ./start.sh

#ENTRYPOINT [ "/bin/bash", "-c", "python iota_service.py -s ${SERVER} -ll ${LOGLEVEL} -a ${IOTA_ADDRESS} -d ${IOTA_DEPTH} -uri ${IOTA_NODE_URI} -seed ${IOTA_SEED} -bs ${KAFKA_BOOTSTRAP_SERVER} -i ${INPUT} -o ${OUTPUT} -e ${ERRORS}" ]
ENTRYPOINT [ "/bin/bash", "-c", "python iota_service.py -s 'KAFKA' -ll 'DEBUG' -a '9E99GKDY9BYDQ9PGOHHMUWJLBDREMK9BVHUFRHVXCVUIFXLNTZMXRM9TDXJKZDAKIGZIMCJSH9Q9V9GKW' -d '2' -uri 'https://nodes.devnet.thetangle.org:443' -seed 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' -bs 'kafka.core-dev:9092' -i 'com.ubirch.iota' -o 'com.ubirch.eventlog.encoder' -e 'com.ubirch.iota_error'" ]
#ENTRYPOINT [ "/bin/bash", "-c", "python iota_service.py -s 'KAFKA' -ll 'DEBUG' -a '9E99GKDY9BYDQ9PGOHHMUWJLBDREMK9BVHUFRHVXCVUIFXLNTZMXRM9TDXJKZDAKIGZIMCJSH9Q9V9GKW' -d '2' -uri 'https://nodes.devnet.thetangle.org:443' -seed 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' -bs 'host.docker.internal:9092' -i 'com.ubirch.iota' -o 'com.ubirch.eventlog.encoder' -e 'com.ubirch.iota_error'" ]
