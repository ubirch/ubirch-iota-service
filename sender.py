#Sends a message (STRING) into queue1 (one by one)


# Connects to the elasticMQServer and retrieves a queue
# See custom.conf for more details

import Library.ElasticMQ_Connection as EMQ

url = 'http://localhost:9324'
client = EMQ.connect(url)
queue1 = EMQ.getQueue(url, 'queue1')


def send(queue, msg):
    return queue.send_message(
        MessageBody=(
            msg

        )
    )


send(queue1, 'Hallo')