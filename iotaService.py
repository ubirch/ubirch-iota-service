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
import serviceLibrary as service


args = service.set_arguments("IOTA")

url = args.url
region = args.region
aws_secret_access_key = args.accesskey
aws_access_key_id = args.keyid

queue1 = EMQ.getQueue('queue1', url, region, aws_secret_access_key, aws_access_key_id)
queue2 = EMQ.getQueue('queue2', url, region, aws_secret_access_key, aws_access_key_id)
errorQueue = EMQ.getQueue('errorQueue', url, region, aws_secret_access_key, aws_access_key_id)



#TODO: WALLET MANAGEMENT


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


def generateAddress():
    gna_result = api.get_new_addresses(count=1)
    addresses = gna_result['addresses']
    return addresses


receiver_address = generateAddress()[0]
print('receiver address = ' + str(receiver_address))


# Anchors a hash from queue1
# Sends the TxID + hash (json file) in queue2 and errors are sent in errorQueue
# Runs continuously (check if messages are available in queue1)



# We assume the string will not exceed 2187 Trytes as it is supposed to be a hash with a short fixed length

def storeStringIOTA(string):
    if service.is_hex(string):
        message = TryteString.from_unicode(string)  # Note: if message > 2187 Trytes, it is sent in several transactions
        proposedTransaction = ProposedTransaction(
            address=Address(receiver_address),
            value=0,
            message=message
        )
        transfer = api.send_transfer(  # Execution of the transaction = only time consuming operation
            depth=depth,
            transfers=[proposedTransaction],
        )

        txhash = str(getTransactionHashes(transfer)[0])
        print({'txid': txhash, 'message': string})

        return {'txid': txhash, 'message': string}

    else:
        return False


def getTransactionHashes(transfer):
    transactionHash = []
    for transaction in transfer["bundle"]:  # Bundle of transaction published on the Tangle
        transactionHash.append(transaction.hash)
    return transactionHash


def main(storefunction):
    """Continuously polls the queue for messages"""
    while True:
        service.poll(queue1, errorQueue, queue2, storefunction)


main(storeStringIOTA)

