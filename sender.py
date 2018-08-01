#Sends a message (STRING) into queue1 (one by one)


# Connects to the elasticMQServer and retrieves a queue
import sys
sys.path.insert(0, 'Library')

import ElasticMQ_Connection as EMQ

url = 'http://localhost:9324'

#client = EMQ.connect(endpoint_url, region_name, aws_secret_access_key, aws_access_key_id)
client = EMQ.connect(url)
queue1 = EMQ.getQueue('queue1')


def send(queue, msg):
    return queue.send_message(
        MessageBody=msg
    )


for i in range(0,20):
    send(queue1, '0123456789ABCDEF' + str(i))



#TODO: INFINITE LOOP TRY CATCH (HASH OF TIME STAMP + RANDOM ERROR )
#TODO: AUTH ARGPARSE IN EACH FILE