# coding: utf-8
import json
import sys

from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction
import random


depth = 6
uri = 'https://testnet140.tangle.works:443'
chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9' #Used to generate the seed

#Converts a Json file into Trytes
def JsontoTrytes(file):
    data = open(file).read()
    dataString = json.dumps(data)
    return TryteString.from_unicode(dataString)

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

def storeJson(file):
    receiver_address = generateAddress()[0]
    sender_address = generateAddress()[1]

    print('receiver address = ', receiver_address)
    print('sender address = ', sender_address)

    sender_account = api.get_account_data(start=0)
    print("sender balance = " + str(sender_account["balance"]))

    # We store the json file into message part of the transaction
    message = JsontoTrytes(file)

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

    print(api.get_latest_inclusion(transactionHash))


try:
    storeJson(sys.argv[1])

except IndexError:
    print("No Json file given!")