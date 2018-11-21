# ubirch-iota-service
A small IOTA based anchoring service. Master sends the messages one by one while fix_storing sends them in a bundle.

This projects is using the IOTA testnet. So far the mainnet does not seem to be production ready.

# Configuration
This projects uses python 2.7. <br>
Please run in your virtual environment:

        pip install -r requirements.txt
       
Moreover, [Kafka](https://kafka.apache.org/) needs to be properly installed.
This projects mainly uses [pyota](https://media.readthedocs.org/pdf/pyota/develop/pyota.pdf)



## How to use this service :

1. Set up the kafka server.

2. Launch the server ( ./start-zookeeper.sh anc ./start-kafka.sh in bin/kafka). Topic creation : ./create-all-topics.sh

4. Once the server is running, start sender.py which will send via an infinite loop messages to the first queue (queue1). Those messages will mainly be hex strings (hashes) but there will be also be non hex-strings which will be processed as errors by the service.

5. Run the service iotaService.py (you can run this script several times to increase the message procession speed). <br> This script will either send errors to the errorQueue or store a Json file {hash : hash ; txid : txid } in the IOTA Tangle and also send it to queue2.

6. Run the two scripts receiver.py and receiver_errors.py which will read messages sent into the two queues.
