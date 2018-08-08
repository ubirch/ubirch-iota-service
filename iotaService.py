# coding: utf-8

import json
import sys
import random
import argparse
import time  # for testing

from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction

sys.path.insert(0, 'Library')
import ElasticMQ_Connection as EMQ

parser = argparse.ArgumentParser(description='Ubirch iota anchoring service')

parser.add_argument('-u', '--url',
                    help="endpoint url of the sqs server, input localhost:9324 for local connection (default)",
                    metavar="URL", type=str, default="http://localhost:9324")
parser.add_argument('-r', '--region', help="region name of sqs server, (default : 'elasticmq' for local)",
                    metavar="REGION", type=str, default="elasticmq")
parser.add_argument('-ak', '--accesskey', help="AWS secret access key, input 'x'for local connection (default)",
                    metavar="SECRETACCESSKEY", type=str, default="x")
parser.add_argument('-ki', '--keyid', help="AWS access key id, input 'x' for local connection (default)",
                    metavar="KEYID", type=str, default="x")

args = parser.parse_args()

url = args.url
region = args.region
aws_secret_access_key = args.accesskey
aws_access_key_id = args.keyid

queue1 = EMQ.getQueue('queue1', url, region, aws_secret_access_key, aws_access_key_id)
queue2 = EMQ.getQueue('queue2', url, region, aws_secret_access_key, aws_access_key_id)
errorQueue = EMQ.getQueue('errorQueue', url, region, aws_secret_access_key, aws_access_key_id)

chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'  # Used to generate the seed


# Seed generator
def generateSeed():
    seed = ''
    for i in range(81): seed += random.choice(chars)
    return seed


seed = b'OF9JOIDX9NVXPQUNQLHVBBNKNBVQGMWHIRZBGWJOJLRGQKFMUMZFGAAEQZPXSWVIEBICOBKHAPWYWHAUF'

depth = 6
uri = 'https://nodes.devnet.iota.org:443'
api = Iota(uri, seed=seed)
print("node info : " + str(api.get_node_info()))


##############################################TODO: WALLET MANAGEMENT


def generateAddress():
    gna_result = api.get_new_addresses(count=1)
    addresses = gna_result['addresses']
    return addresses


receiver_address = generateAddress()[0]
print('receiver address = ' + str(receiver_address))


##########################################


# Anchors a hash from from queue1
# Sends the TxID + hash (json file) in queue2 and errors are sent in errorQueue

# Runs continuously (check if messages are available in queue1)


def send(queue, msg):
    return queue.send_message(
        MessageBody=msg
    )


def storeString(string):
    if is_hex(string):
        message = TryteString.from_unicode(string)  # if message > 2187 Trytes, it is sent in several transactions
        proposedTransaction = ProposedTransaction(
            address=Address(receiver_address),
            value=0,
            message=message
        )
        transfer = api.send_transfer(  # Execution of the transaction
            depth=depth,
            transfers=[proposedTransaction],
        )
        return getTransactionHashes(transfer)

    else:
        return False


def getTransactionHashes(transfer):
    transactionHash = []
    for transaction in transfer["bundle"]:  # Bundle of transaction published on the Tangle
        transactionHash.append(transaction.hash)
        print(transaction.address, transaction.hash)
    return transactionHash


def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def main(queue_name):
    """Continuously polls the queue for messages"""
    while True:
        poll(queue=queue_name)


def poll(queue):
    start = time.time()
    messages = queue.receive_messages()  # Note: MaxNumberOfMessages default is 1.
    start2 = time.time()
    print("receiving time : " + str(start2 - start))
    for m in messages:
        start3 = time.time()
        process_message(m)
        print("processing time = " + str(time.time() - start3))

def process_message(m):
    a = time.time()
    storing = storeString(m.body)
    print("storing = " + str(time.time() - a))
    if storing == False:
        json_error = json.dumps({"Not a hash" : m.body})
        b = time.time()
        send(errorQueue, json_error)
        print("sending error = " + str(time.time() - b))

    else:
        transactionHashes = storing
        for txid in transactionHashes:  # In case of the anchoring results in several transactions
            json_data = json.dumps({"tx" : str(txid), "hash" : m.body})
            c = time.time()
            send(queue2, json_data)
            print("sending message= " + str(time.time() - c))

    m.delete()


main(queue1)

