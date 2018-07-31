#Retrieves the message sent (queue1) (one by one) and deletes them once read

import Library.ElasticMQ_Connection as EMQ

url = 'http://localhost:9324'

queue1 = EMQ.getQueue(url, 'queue1')
queue2 = EMQ.getQueue(url, 'queue2')
errorQueue = EMQ.getQueue(url, 'errorQueue')

#
def receive(queue):
    messages = queue.receive_messages(MaxNumberOfMessages=10)  # Note: MaxNumberOfMessages default is 1.
    for m in messages:
        print(m.body)
        print(len(messages))

receive(queue=queue1)
