# coding: utf-8

import json
import sys
import random
import boto3
import argparse
import time

from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction


sys.path.insert(0, 'Library')
import ElasticMQ_Connection as EMQ
import sender

#TODO : reduce anchoring time

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



depth = 6
uri = 'https://testnet140.tangle.works:443'
chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' #Used to generate the seed



#Anchors the HASH of the message received in queue1
#Sends the TxID in queue2
#Runs continuously (check if messages are available in queue1)



#Seed generator
def generateSeed():
    seed = ''
    for i in range(81): seed += random.choice(chars)
    return seed


sender_seed = b'OF9JOIDX9NVXPQUNQLHVBBNKNBVQGMWHIRZBGWJOJLRGQKFMUMZFGAAEQZPXSWVIEBICOBKHAPWYWHAUF'
receiver_seed = b'DBWJNNRZRKRSFAFRZDDKAUFSZCTDZHJXDLHVCEVQKMFHN9FYEVNJS9JPNFCLXNKNWYAJ9CUQSCNHTBWWB'


api = Iota(uri, seed=sender_seed)
print(api.get_node_info())

#TODO: WALLET MANAGEMENT

def generateAddress():
    gna_result = api.get_new_addresses(count=2)
    addresses = gna_result['addresses']
    return addresses



def storeString(string):
    receiver_address = generateAddress()[0]
    sender_address = generateAddress()[1]

    print('receiver address = ', receiver_address)
    print('sender address = ', sender_address)

    sender_account = api.get_account_data(start=0)
    print("sender balance = " + str(sender_account["balance"]))

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
            inputs=[Address(sender_address, key_index=0, security_level=2)] #ignored for 0 value transfers
        )

        return getTransactionHashes(transfer)

    else:
        print(string + " is not a hash")


def getTransactionHashes(transfer):
    transactionHash = []
    for transaction in transfer["bundle"]:  # Bundle of transaction published on the Tangle
        transactionHash.append(transaction.hash)
        print(transaction.address, transaction.hash)

    inclusionState = api.get_latest_inclusion(transactionHash)
    print("latest inclusion state : " + str(inclusionState))

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


#Messages are written 1 by 1 so we receive them on by one


def poll(queue):
    messages = queue.receive_messages(MaxNumberOfMessages=10)  # Note: MaxNumberOfMessages default is 1.
    #queue.delete_messages()          #TODO Clear the queue1 after reading
    for m in messages:
        transactionHashes = storeString(m.body)
        for txid in transactionHashes: #In case of the anchoring results in several transactions
            json_data = json.dumps({str(txid) : m.body})
            sender.send(queue2, json_data)


main(queue1)



