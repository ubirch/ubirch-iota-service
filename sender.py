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

from ubirch.anchoring import *
import time
import hashlib

from kafka import KafkaProducer


args = set_arguments("IOTA")
port = args.port

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def publish_message(producer, topic_name, value):
    try:
        value_bytes = bytes(value)
        producer.send(topic_name, value=value_bytes)
        producer.flush()

    except Exception as ex:

        print('Exception in publishing message')
        print(str(ex))




i = 1
j = 1
while True:
    t = str(time.time()).encode('utf-8')
    message = hashlib.sha256(t).hexdigest()
    if '0' in message[0:8]:                 # Error propagation in queue1
        publish_message(producer, "errorQueue", "error %s" %i)
        print("error %s sent" %i)
        i += 1
        time.sleep(0.1)

    else:                                   # Sends in queue1 the sha256 hash of the time()
        publish_message(producer, 'queue1', message)
        print("message %s sent" % j)
        j += 1
        time.sleep(0.1)
