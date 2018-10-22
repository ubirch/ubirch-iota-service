# coding: utf-8

# Copyright (c) 2018 ubirch GmbH.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
from ubirch.anchoring import *
from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction

from kafka import KafkaConsumer # TO DO :Integrate the package in ubirch-python-utils
from kafka import KafkaProducer


args = set_arguments("IOTA")

url = args.url
region = args.region
aws_secret_access_key = args.accesskey
aws_access_key_id = args.keyid

queue1 = getQueue('queue1', url, region, aws_secret_access_key, aws_access_key_id)
queue2 = getQueue('queue2', url, region, aws_secret_access_key, aws_access_key_id)
errorQueue = getQueue('errorQueue', url, region, aws_secret_access_key, aws_access_key_id)


# TODO: WALLET MANAGEMENT


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


def generateAddress():
    gna_result = api.get_new_addresses(count=1)
    addresses = gna_result['addresses']
    return addresses


receiver_address = generateAddress()[0]
print('receiver address = ' + str(receiver_address))


# We assume the string will not exceed 2187 Trytes as it is supposed to be a hash with a short fixed length

def storeStringIOTA(string):
    if is_hex(string):
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
        print({'status': 'added', 'txid': txhash, 'message': string})

        return {'status': 'added', 'txid': txhash, 'message': string}

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
        poll(queue1, errorQueue, queue2, storefunction)


main(storeStringIOTA)

