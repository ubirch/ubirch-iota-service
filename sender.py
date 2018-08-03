#Sends messages (HASH (hex) into queue1

import sys
import argparse
sys.path.insert(0, 'Library')

import ElasticMQ_Connection as EMQ

#For testing
import time
import hashlib


parser = argparse.ArgumentParser(description='Ubirch iota anchoring service')

parser.add_argument('-u', '--url', help="endpoint url of the sqs server, input localhost:9324 for local connection (default)", metavar="URL", type=str, default="http://localhost:9324")
parser.add_argument('-r', '--region', help="region name of sqs server, (default : 'elasticmq' for local)", metavar="REGION", type=str, default="elasticmq")
parser.add_argument('-ak', '--accesskey', help="AWS secret access key, input 'x'for local connection (default)", metavar="SECRETACCESSKEY", type=str, default="x")
parser.add_argument('-ki', '--keyid', help="AWS access key id, input 'x' for local connection (default)", metavar="KEYID", type=str, default="x")

args = parser.parse_args()

url = args.url
region = args.region
aws_secret_access_key = args.accesskey
aws_access_key_id = args.keyid

queue1 = EMQ.getQueue('queue1', url, region, aws_secret_access_key, aws_access_key_id)


def send(queue, msg):
    return queue.send_message(
        MessageBody=msg
    )


i = 0
j = 0
while True:
    t = str(time.time())
    message = hashlib.sha256(t).hexdigest()
    if '0' in message[0:8]:
        send(queue1, "error %s" %i)
        print("error %s sent" %i)
        time.sleep(1)
        i += 1

    else:
        send(queue1, message)
        print("message %s sent" % j)
        time.sleep(1)
        j += 1
