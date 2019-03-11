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

from iota import TryteString
from iota import Iota
from iota import ProposedTransaction
from iota import Address

from kafka import *
from ubirch.anchoring import *

import logging
from logging.handlers import RotatingFileHandler


"""
    The code below is used to initialize parameters passed in arguments in the terminal.
    Before starting the service one must choose between --server='SQS' or --server='KAFKA' depending on the message
    queuing service desired.
    Depending on the server chosen, several arguments of configuration of the latest are initialized.

"""
args = set_arguments("IOTA")
server = args.server

"""
    Logger & handlers configuration
"""

log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
}


logger = logging.getLogger('ubirch-iota-service')
level = log_levels.get(args.loglevel.lower())
logger.setLevel(level)


# Formatter adding time, name and level of each message when a message is written in the logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler redirecting logs in a file in 'append' mode, with 1 backup and 1Mo max size
file_handler = RotatingFileHandler('iota_service.log', mode='a', maxBytes=1000000, backupCount=1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler on the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


logger.info("You are using ubirch's IOTA anchoring service")

if server == 'SQS':
    logger.info("SERVICE USING SQS QUEUE MESSAGING")

    url = args.url
    region = args.region
    aws_secret_access_key = args.accesskey
    aws_access_key_id = args.keyid

    input_messages = get_queue(args.input, url, region, aws_secret_access_key, aws_access_key_id)
    output_messages = get_queue(args.output, url, region, aws_secret_access_key, aws_access_key_id)
    error_messages = get_queue(args.errors, url, region, aws_secret_access_key, aws_access_key_id)
    producer = None

elif server == 'KAFKA':
    logger.info("SERVICE USING APACHE KAFKA FOR MESSAGING")

    output_messages = args.output
    error_messages = args.errors

    bootstrap_server = args.bootstrap_server
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    input_messages = KafkaConsumer(args.input, bootstrap_servers=bootstrap_server)


"""

    We now chose an IOTA node, and initialize an iota.Iota object with the URI of the node, and optional seed.
    If no seed is specified, a random one will be generated

    The depth determines how deep the tangle is analysed for getting Tips. The higher the Depth, the longer will it take
    to analyze the tangle, but older transactions will receive a higher chance of confirmation.
    Uri is the uri of the IOTA node.

"""
address = args.address
depth = args.depth
seed = args.seed
uri = args.uri

api = Iota(uri, seed=seed)


logger.info('address used = %s, seed used: %s \n' % (str(address), str(seed)))


def store_iota(string):
    """
    We assume the string will not exceed 2187 Trytes as it is supposed to be a hash with a short fixed length

    :param string: message to be sent in the IOTA transaction
    :return: If the input string is hexadecimal : a dictionary containing the string sent in the transaction
    and the transaction hash.
            If not : False
    :rtype: Dictionary if the input string is hexadecimal or boolean if not.

    """
    if is_hex(string):
        message = TryteString.from_unicode(string)  # Note: if message > 2187 Trytes, it is sent in several transactions
        logger.debug("'%s' ready to be sent" % string)
        proposed_transaction = ProposedTransaction(
            address=Address(address),
            value=0,
            message=message
        )
        transfer = api.send_transfer(  # Execution of the transaction = only time consuming operation
            depth=depth,
            transfers=[proposed_transaction],
        )
        tx_hash = str(get_transaction_hashes(transfer)[0])

        logger.debug("'%s' sent" % string)
        logger.info({'status': 'added', 'txid': tx_hash, 'message': string})
        return {'status': 'added', 'txid': tx_hash, 'message': string}

    else:
        logger.warning({"Not a hash": string})
        return False


def get_transaction_hashes(transfer):
    """
    Each bundle has the following attributes:

    hash: BundleHash: The hash of this bundle. This value is generated by taking a hash of the metadata from all transactions in the bundle.
    is_confirmed: Optional[bool]: Whether the transactions in this bundle have been confirmed. Refer to the Basic Concepts section for more information.
    tail_transaction: Optional[Transaction]: The bundle’s tail transaction.
    transactions: List[Transaction]: The transactions associated with this bundle.


    :param transfer: send_transfer prepares a set of transfers and creates the bundle,
    then attaches the bundle to the Tangle, and broadcasts and stores the transactions.
    :return: send_transfer returns a dict with the following items: bundle: Bundle: The newly-published bundle.

    :rtype: dict

    """
    transaction_hash = []
    for transaction in transfer["bundle"]:  # Bundle of transaction published on the Tangle
        transaction_hash.append(transaction.hash)
    return transaction_hash


def main(store_function):
    """

    Continuously polls the queue1 for messages and processes them in queue2 (sends the dict returned by storestringIOTA)
    or error_queue

    :param store_function: Defines the service used to anchor the messages. Here it is IOTA.

    """
    while True:
        poll(input_messages, error_messages, output_messages, store_function, server, producer)


main(store_iota)

