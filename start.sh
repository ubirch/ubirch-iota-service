#!/usr/bin/env sh

python iota_service.py -s "${SERVER}" -ll "${LOGLEVEL}" -nt "${NETWORKTYPE}" -ni "${NETWORKINFO}" -a "${IOTA_ADDRESS}" -d "${IOTA_DEPTH}" -uri "${IOTA_NODE_URI}" -seed "${IOTA_SEED}" -bs "${KAFKA_BOOTSTRAP_SERVER}" -i "${INPUT}" -o "${OUTPUT}" -e "${ERRORS}"

#  -u "${SQS_URL}" -r "${SQS_REGION}" -ak "${SQS_SECRET_ACCESS_KEY}" -ki "${SQS_KEY_ID}"
