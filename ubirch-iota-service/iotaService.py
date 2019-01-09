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
from iota import TryteString
from iota import Iota
from iota import Address
from iota import ProposedTransaction

from kafka import *
from ubirch.anchoring import *

"""
    The code below is used to initialize paramaters passed in arguments in the terminal.
    Before starting the service one must choose between --server='SQS' or --server='KAFKA' depending on the message
    queuing service desired.
    Depending on the server chosen, several arguments of configuration of the latest are initialized.

"""

args = set_arguments("IOTA")
server = args.server

if server == 'SQS':
    print("SERVICE USING SQS QUEUE MESSAGING")
    url = args.url
    region = args.region
    aws_secret_access_key = args.accesskey
    aws_access_key_id = args.keyid
    queue1 = getQueue('queue1', url, region, aws_secret_access_key, aws_access_key_id)
    queue2 = getQueue('queue2', url, region, aws_secret_access_key, aws_access_key_id)
    errorQueue = getQueue('errorQueue', url, region, aws_secret_access_key, aws_access_key_id)
    producer = None

elif server == 'KAFKA':
    print("SERVICE USING APACHE KAFKA FOR MESSAGING")
    port = args.port
    producer = KafkaProducer(bootstrap_servers=port)
    queue1 = KafkaConsumer('queue1', bootstrap_servers=port)
    queue2 = None
    errorQueue = None


def generateSeed():
    """
        This function generates an IOTA seed of fixed length 81 using the set of characters 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'

        :return: Seed is being used to derive private keys from, and thus for signing transactions.
        :rtype: str

        .. note:: Function used only once to generate the seed.
    """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'  # List of characters used to generate the seed
    seed = ''
    for i in range(81): seed += random.choice(chars)
    return seed


"""

    We now chose an IOTA node, and initialize an iota.Iota object with the URI of the node, and optional seed.
    
    The depth determines how deep the tangle is analysed for getting Tips. The higher the Depth, the longer will it take
    to analyze the tangle, but older transactions will receive a higher chance of confirmation.
    Uri is the uri of the IOTA node.
    
"""
Seed = b'OF9JOIDX9NVXPQUNQLHVBBNKNBVQGMWHIRZBGWJOJLRGQKFMUMZFGAAEQZPXSWVIEBICOBKHAPWYWHAUF'
depth = 6
uri = 'https://nodes.devnet.iota.org:443'
api = Iota(uri, seed=Seed)


def generateAddress():
    """
        Function used to generate a new IOTA address.

        :return: A valid IOTA address
        :rtype <class 'iota.types.Address'>

    """
    gna_result = api.get_new_addresses(count=1)
    addresses = gna_result['addresses']
    return addresses

"""
    We only need one IOTA address to make the service work
"""
receiver_address = generateAddress()[0]
print('receiver address = ' + str(receiver_address))



def storeStringIOTA(string):
    """
    # We assume the string will not exceed 2187 Trytes as it is supposed to be a hash with a short fixed length

    :param string: message to be sent in the IOTA transaction
    :return: If the input string is hexadecimal : a dictionnary containing the string sent in the transaction
    and the transaction hash.
            If not : False
    :rtype: Dictionary if the input string is hexadecimal or boolean if not.
    """
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
        print("message : '%s' sent" % (string))
        return {'status': 'added', 'txid': txhash, 'message': string}

    else:
        return False


def getTransactionHashes(transfer):
    """

    :param transfer:
    :return:
    """
    transactionHash = []
    for transaction in transfer["bundle"]:  # Bundle of transaction published on the Tangle
        transactionHash.append(transaction.hash)
    return transactionHash


def main(storefunction):
    """
    Continuously polls the queue1 for messages and processes them in queue2 (sends the dict returned by storestringIOTA)
    or errorQueue

    :param storefunction: Defines the service used to anchor the messages. Here it is IOTA.
    """
    while True:
        poll(queue1, errorQueue, queue2, storefunction, server, producer)


main(storeStringIOTA)

