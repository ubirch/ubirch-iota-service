# ubirch-iota-service
A small IOTA based anchoring service. This projects is using the IOTA testnet.

# Configuration
This projects uses python 3.6. <br>
Please run in your virtual environment:

        pip install -r requirements.txt
       
This projects mainly uses [pyota](https://media.readthedocs.org/pdf/pyota/develop/pyota.pdf)

## How to use this service :

1. Please install [Elasticmq](https://github.com/adamw/elasticmq) and/or [Kafka](https://kafka.apache.org/)
in a folder called "dependencies" (respect the name so the scripts in bin/ work properly)


3. Useful scripts are in bin/ <br>
    a) In elasticMQ/: ./start-elasticMQ.sh : to run the ElasticMQ server <br>
    
    b) In kafka/: ./start_zookeeper.sh then ./start-kafka.sh and ./create-all-topics.sh : to run the Kafka server and create the topics.<br>

        
4. Then, in a terminal, run in ubirch-iota-service/ the scripts sender.py then receiver.py and receiver_errors.py with the flag --server='SQS' or --server='KAFKA'<br>

Finally, start the service (which you can run multiple times to increase efficiency) :

        python iotaService.py --server=('SQS' or 'KAFKA')
