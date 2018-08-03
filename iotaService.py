# coding: utf-8

import json
import sys
import random
import argparse
import time #for testing

from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction


sys.path.insert(0, 'Library')
import ElasticMQ_Connection as EMQ

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
queue2 = EMQ.getQueue('queue2', url, region, aws_secret_access_key, aws_access_key_id)
errorQueue = EMQ.getQueue('errorQueue', url, region, aws_secret_access_key, aws_access_key_id)



chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' #Used to generate the seed

#Seed generator
def generateSeed():
    seed = ''
    for i in range(81): seed += random.choice(chars)
    return seed


seed = b'OF9JOIDX9NVXPQUNQLHVBBNKNBVQGMWHIRZBGWJOJLRGQKFMUMZFGAAEQZPXSWVIEBICOBKHAPWYWHAUF'

depth = 6
uri = 'https://testnet140.tangle.works:443'
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


#Anchors a hash from from queue1
#Sends the TxID + hash (json file) in queue2 and errors are sent in errorQueue

#Runs continuously (check if messages are available in queue1)



def send(queue, msg):
    return queue.send_message(
        MessageBody=msg
    )




def storeString(string):
    if is_hex(string):
        # We store the string into message part of the transaction
        message = TryteString.from_unicode(string)
        # if message > 2187 Trytes, it is sent in several transactions

        proposedTransaction = ProposedTransaction(
            address=Address(receiver_address),
            value=0,
            message=message
        )

        # Execution of the transaction
        transfer = api.send_transfer(
            depth=depth,
            transfers=[proposedTransaction],
        )

        return getTransactionHashes(transfer)

    else:
        return string


def getTransactionHashes(transfer):
    transactionHash = []
    for transaction in transfer["bundle"]:  # Bundle of transaction published on the Tangle
        transactionHash.append(transaction.hash)
        print(transaction.address, transaction.hash)
        #print(transaction.hash)

    inclusionState = api.get_latest_inclusion(transactionHash)
    #print("latest inclusion state : " + str(inclusionState))

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
    messages = queue.receive_messages(MaxNumberOfMessages=10)         # Note: MaxNumberOfMessages default is 1.
    for m in messages:
        if type(storeString(m.body)) == str:
            json_error = json.dumps({"ValueError" : m.body})
            send(errorQueue, json_error)
        else:
            transactionHashes = storeString(m.body)
            for txid in transactionHashes:          #In case of the anchoring results in several transactions
                json_data = json.dumps({str(txid) : m.body})
                send(queue2, json_data)
        m.delete()


main(queue1)



