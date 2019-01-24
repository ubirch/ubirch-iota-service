#!/usr/bin/env bash

python iota_service.py -s ${SERVER} -ll ${LOGLEVEL} -a ${IOTA_ADDRESS} -d ${IOTA_DEPTH} -uri ${IOTA_NODE_URI} -seed ${IOTA_SEED} -p ${KAFKA_PORT} -u ${SQS_URL} -r ${SQS_REGION} -ak ${SQS_SECRET_ACCESS_KEY} -ki ${SQS_KEY_ID}
