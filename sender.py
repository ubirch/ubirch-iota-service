import boto3
import Library.ElasticMQ_Connection as EMQ
import time as t

url = 'http://localhost:9324'

#Connects to the elasticMQServer and retrieves a queue
#See custom.conf for more details

client = EMQ.connect(url)
queue1 = EMQ.getQueue(url, 'queue1')


def send(i):
    return queue1.send_message(
        MessageBody=(
            'Hallo Ubirch : ' + str(i)
        )
    )
i=0
N = 1000
while N>0:
    N = N - 1
    i = i +1
    send(i)
