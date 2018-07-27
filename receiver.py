import Library.ElasticMQ_Connection as EMQ

url = 'http://localhost:9324'

queue1 = EMQ.getQueue(url, 'queue1')


def poll(queue):
    messages = queue.receive_messages(MaxNumberOfMessages=10)  # Note: MaxNumberOfMessages default is 1.
    for m in messages:
        print(m.body)


poll(queue=queue1)
