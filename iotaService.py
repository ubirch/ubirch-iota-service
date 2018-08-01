# coding: utf-8

import json
import sys
import random
import boto3

from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction


sys.path.insert(0, 'Library')
import ElasticMQ_Connection as EMQ
import sender



depth = 6
uri = 'https://testnet140.tangle.works:443'
chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' #Used to generate the seed

url = 'http://localhost:9324'
queue1 = EMQ.getQueue('queue1')
queue2 = EMQ.getQueue('queue2')
errorQueue = EMQ.getQueue('errorQueue')

client = boto3.resource('sqs',
                        endpoint_url=url,  #
                        region_name="elasticmq",  #
                        aws_secret_access_key='x',  # parameters
                        aws_access_key_id='x',  #
                        use_ssl=False)

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

    # We store the string into message part of the transaction
    message = TryteString.from_unicode(string)
    #if message > 2187 Trytes, it is sent in different transactions

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

    transactionHash = []
    for transaction in transfer["bundle"]: #Bundle of transaction published on the Tangle
        transactionHash.append(transaction.hash)
        print(transaction.address, transaction.hash)

    inclusionState = api.get_latest_inclusion(transactionHash)
    print("latest inclusion state : " + str(inclusionState))

    return transactionHash  #LIST : To be sent in queue2



def main(queue_name):
    """Continuously poll the queue for messages"""
    while True:
        poll(queue=queue_name)


#Messages are written 1 by 1 so we receive them on by one
def poll(queue):
    messages = queue.receive_messages()  # Note: MaxNumberOfMessages default is 1.
#   queue.delete_message()          #TODO Clear the queue1 after reading
    for m in messages:
        hashed_data = str(hash(m.body)) #TODO : better hashing fct
        transactionHashes = storeString(hashed_data)
        for txid in transactionHashes:
            sender.send(queue2, str(txid))


poll(queue1)



