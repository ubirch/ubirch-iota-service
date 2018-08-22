# coding: utf-8
import sys
sys.path.insert(0, 'Library')

import ElasticMQ_Connection as EMQ
import serviceLibrary as service

# Retrieves error messages

args = service.set_arguments("ethereum")
url = args.url
region = args.region
aws_secret_access_key = args.accesskey
aws_access_key_id = args.keyid

errorQueue = EMQ.getQueue('errorQueue', url, region, aws_secret_access_key, aws_access_key_id)

while True:
    errors = errorQueue.receive_messages()
    for e in errors:
        print(e.body)
        e.delete()

