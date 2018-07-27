import Library.ElasticMQ_Connection as EMQ

url = 'http://localhost:9324'

#Connects to the elasticMQServer and retrieves a queue
#See custom.conf for more details

client = EMQ.connect(url)
queue1 = EMQ.getQueue(url, 'queue1')


def send():
    return queue1.send_message(
        MessageBody=(
            'Hallo Ubirch'
        )
    )


send()