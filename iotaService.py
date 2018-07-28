# coding: utf-8

#Anchors the HASH of the message received in queue1
#Sends the TxID in queue2
#Runs continuously (check if messages are available in queue1)

import receiver

import json
import sys
import random

from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction

import Library.ElasticMQ_Connection as EMQ



depth = 6
uri = 'https://testnet140.tangle.works:4'
chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' #Used to generate the seed


url = 'http://localhost:9324'
queue1 = EMQ.getQueue(url, 'queue1')
queue2 = EMQ.getQueue(url, 'queue2')
errorQueue = EMQ.getQueue(url, 'errorQueue')


def main(queue_name):
    """Continuously poll the queue for messages"""
    while True:
        poll(queue=queue_name)


def poll(queue): #Messages are written 1 by 1 so we receive them on by one
    #messages = queue.receive_messages()
    messages = queue.receive_messages(MaxNumberOfMessages=10)  # Note: MaxNumberOfMessages default is 1.
    for m in messages:
        print(m.body)
#        storeString(m.body)






#Converts a Json file into Trytes

# def JsontoTrytes(file):
#     data = open(file).read()
#     dataString = json.dumps(data)
#     return TryteString.from_unicode(dataString)


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

# def storeJson(file):
#     receiver_address = generateAddress()[0]
#     sender_address = generateAddress()[1]
#
#     print('receiver address = ', receiver_address)
#     print('sender address = ', sender_address)
#
#     sender_account = api.get_account_data(start=0)
#     print("sender balance = " + str(sender_account["balance"]))
#
#     # We store the json file into message part of the transaction
#     message = JsontoTrytes(file)
#
#     proposedTransaction = ProposedTransaction(
#         address=Address(receiver_address),
#         value=0,
#         message=message
#     )
#
#     # Execution of the transaction
#     transfer = api.send_transfer(
#         depth=depth,
#         transfers=[proposedTransaction],
#         inputs=[Address(sender_address, key_index=0, security_level=2)]
#     )
#
#     transactionHash = []
#     for transaction in transfer["bundle"]:
#         transactionHash.append(transaction.hash)
#         print(transaction.address, transaction.hash)
#
#     print(api.get_latest_inclusion(transactionHash))


def storeString(string):
    receiver_address = generateAddress()[0]
    sender_address = generateAddress()[1]

    print('receiver address = ', receiver_address)
    print('sender address = ', sender_address)

    sender_account = api.get_account_data(start=0)
    print("sender balance = " + str(sender_account["balance"]))

    # We store the string into message part of the transaction
    message = TryteString.from_unicode(string) #Conversion

    proposedTransaction = ProposedTransaction(
        address=Address(receiver_address),
        value=0,
        message=message
    )

    # Execution of the transaction
    transfer = api.send_transfer(
        depth=depth,
        transfers=[proposedTransaction],
        inputs=[Address(sender_address, key_index=0, security_level=2)]
    )

    transactionHash = []
    for transaction in transfer["bundle"]:
        transactionHash.append(transaction.hash)
        print(transaction.address, transaction.hash)

    txId = api.get_latest_inclusion(transactionHash)
    print(txId)
    return txId #To be sent in queue2

#Send also error in errorQueue (message > 2187 trytes etc)


# try:
#     storeString(sys.argv[1])
#
# except IndexError:
#     print("No string given!")