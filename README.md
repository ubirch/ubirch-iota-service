# ubirch-iota-service
An IOTA based anchoring service. This projects is using the IOTA testnet.<br>
Please check the [IOTA testnet explorer](https://devnet.thetangle.org/) to look for transactions or addresses.

Default address used in the service:
**9E99GKDY9BYDQ9PGOHHMUWJLBDREMK9BVHUFRHVXCVUIFXLNTZMXRM9TDXJKZDAKIGZIMCJSH9Q9V9GKW**<br>
Click [here](https://devnet.thetangle.org/address/9E99GKDY9BYDQ9PGOHHMUWJLBDREMK9BVHUFRHVXCVUIFXLNTZMXRM9TDXJKZDAKIGZIMCJSH9Q9V9GKW) to see all transactions made with this address.

To setup a new address, please run: *generate_address.py* and pass the address generated as argument in the CLI.

## Configuration

This projects uses python 3.6. <br>
Please run in your virtual environment:
   ```bash
        pip install -r requirements.txt
   ```
       
This projects mainly uses [pyota](https://media.readthedocs.org/pdf/pyota/develop/pyota.pdf)
,the official Python library for the IOTA Core.


## How to use this service

1. Please install [Elasticmq](https://github.com/adamw/elasticmq) and/or [Kafka](https://kafka.apache.org/).
Please respect the following folder structure: <br>

        dependencies/
        ├── elasticMQServer
        │   ├── custom.conf
        │   └── elasticmq-server.jar
        └── kafka
            ├── bin
            │   ├── ...
            ├── config
            │   ├── ...
            ├── libs
            │   ├──...
            ├── LICENSE
            ├── NOTICE
            └── site-docs
                └── ...

And custom.conf should look like this:

        include classpath("application.conf")
        
        // What is the outside visible address of this ElasticMQ node
        // Used to create the queue URL (may be different from bind address!)
        node-address {
            protocol = http
            host = localhost
            port = 9324
            context-path = ""
        }
        
        rest-sqs {
            enabled = true
            bind-port = 9324
            bind-hostname = "0.0.0.0"
            // Possible values: relaxed, strict
            sqs-limits = strict
        }
        
        // Should the node-address be generated from the bind port/hostname
        // Set this to true e.g. when assigning port automatically by using port 0.
        generate-node-address = false
        
        queues {
        
          queue1 {
            defaultVisibilityTimeout = 10 seconds
            receiveMessageWait = 0 seconds
            deadLettersQueue {
                name = "queue1-dead-letters"
                maxReceiveCount = 10 // from 1 to 1000
            }
          }
        
            queue2 {
            defaultVisibilityTimeout = 10 seconds
            receiveMessageWait = 0 seconds
            deadLettersQueue {
                name = "queue2-dead-letters"
                maxReceiveCount = 10 // from 1 to 1000
            }
          }
        
            error_queue {
            defaultVisibilityTimeout = 10 seconds
            receiveMessageWait = 0 seconds
            deadLettersQueue {
                name = "error_queue-dead-letters"
                maxReceiveCount = 10 // from 1 to 1000
            }
          }
        
        }
        


2. Useful scripts are in *bin/* <br>
    a) In *bin/elasticMQ/*, to run the ElasticMQ server: <br>
      ```bash
      ./start-elasticMQ.sh
      ```
       
    b) In *bin/kafka/*, to run the Kafka server and create the topics, execute successively: <br>
     ```bash

        ./start_zookeeper.sh
        ./start-kafka.sh
        ./create-all-topics.sh
     
    ```
      

        
3. Then, in a terminal, run successicely in *ubirch-iota-service/*, the scripts *sender.py* then *receiver.py*
and *receiver_errors.py*, with the flag **--server='SQS'** or **--server='KAFKA'**<br><br>

4. Finally, start the service.<br>

    ```bash
    python iotaService.py --server='SQS'
    ```
    Or:

   ```bash
    python iotaService.py --server='KAFKA'
   ```
    Where:
    - --server='SQS' to use elasticMQ's SQS queuing service
    - --server='KAFKA' to use Apache's Kafka messaging service.
    
    You can run it multiple times to increase throughput.<br>
    
    

## Logs


Once the service is running, logs are recorded in *iota_service.log*

# License 

This project is publicized under the [Apache License 2.0](LICENSE).

