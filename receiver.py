#Retrieves Json (message sent + txid) & error messages after anchoring into the IOTA Blockchain

import sys
sys.path.insert(0, 'Library')
import ElasticMQ_Connection as EMQ
import argparse
import time



parser = argparse.ArgumentParser(description='Ubirch iota anchoring service')

parser.add_argument('-u', '--url', help="endpoint url of the sqs server, input localhost:9324 for local connection (default)", metavar="URL", type=str, default="http://localhost:9324")
parser.add_argument('-r', '--region', help="region name of sqs server, (default : 'elasticmq' for local)", metavar="REGION", type=str, default="elasticmq")
parser.add_argument('-ak', '--accesskey', help="AWS secret access key, input 'x' for local connection (default)", metavar="SECRETACCESSKEY", type=str, default="x")
parser.add_argument('-ki', '--keyid', help="AWS access key id, input 'x' for local connection (default)", metavar="KEYID", type=str, default="x")

args = parser.parse_args()

url = args.url
region = args.region
aws_secret_access_key = args.accesskey
aws_access_key_id = args.keyid


queue2 = EMQ.getQueue('queue2', url, region, aws_secret_access_key, aws_access_key_id)

#
# while True:
#     start = time.time()
#     response = queue2.receive_messages()
#     start2 = time.time()
#     print("receiving time =  " + str( start2 - start))
#     for r in response:
#         print(r.body)
#         r.delete()
#         print("deletion time = " + str(time.time() - start2))



start = time.time()
response = queue2.receive_messages()
start2 = time.time()
print("receiving time =  " + str( start2 - start))
for r in response:
    print(r.body)
    r.delete()
    print("deletion time = " + str(time.time() - start2))
