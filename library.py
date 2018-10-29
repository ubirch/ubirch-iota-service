# temporary lib used until integration in ubirch-python-utils

from kafka import *
import json
import argparse

def producerInstance(port):
    """Creates an instance of a producer """
    producer_instance = KafkaProducer(bootstrap_servers=port)
    return producer_instance


def consumerInstance(topics, port):
    """Creates an instance of consumer of a defined topic """
    consumer_instance = KafkaConsumer(topics, bootstrap_servers=port)
    return consumer_instance


def set_arguments(servicetype):
    parser = argparse.ArgumentParser(description="Ubirch " + servicetype + " anchoring service")
    parser.add_argument('-p', '--port',
                        help="port of the producer or consumer, default is 9092",
                        metavar="PORT", type=list, default=['localhost:9092'])
    parser.add_argument('-kf', '--keyfile', help='location of your keyfile', metavar='PATH TO KEYFILE', type=str)

    return parser.parse_args()


def send(producer, topic, message):
    """ Sends a message to the topic via the producer and then flushes"""
    message_bytes = bytes(message)
    if type(topic) == bytes:
        topic = topic.decode('utf-8')
    producer.send(topic, message_bytes)
    producer.flush()


def is_hex(s):
    """Tests if the string s is hex (True) or not (False)"""
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


# storefunction should always return either False is the string is non-hex or a dict containing {'txid': hash, 'hash': string}
def process_message(message, errorQueue, queue2, storefunction, producer):
    """Anchors the message m in a DLT specified by the storefunction parameter.
    Sends error (non hex message and timeouts) in the errorQueue.
    Sends JSON docs containing the txid and the input data in queue2 if the anchoring was successful"""

    storingResult = storefunction(message) #Anchoring of the message body
    if storingResult == False:
        json_error = json.dumps({"Not a hash": message})
        send(producer, errorQueue, json_error)

    elif storingResult['status'] == 'timeout':
        json_error = json.dumps(storingResult)
        send(producer, errorQueue, json_error)

    else:
        json_data = json.dumps(storingResult)
        send(producer, queue2, json_data)


def poll(queue1, errorQueue, queue2, storefunction, producer):
    """Process messages received from queue1"""
    for m in queue1:
        message = m.value
        process_message(message, errorQueue, queue2, storefunction, producer)

