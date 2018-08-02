
# Connects to the elasticMQServer and retrieves a queue
import sys
sys.path.insert(0, 'Library')
import ElasticMQ_Connection as EMQ
import argparse

url = 'http://localhost:9324'

#client = EMQ.connect(endpoint_url, region_name, aws_secret_access_key, aws_access_key_id)
client = EMQ.connect(url)
queue2 = EMQ.getQueue('queue2')




for i in range(0,20):
    response = queue2.receive_messages()
    for m in response:
        print(m.body)


    # response = queue2.delete_messages(
    #     Entries=[
    #         {
    #             'Id': 'string',
    #             'ReceiptHandle': 'string'
    #         },
    #     ]
    # )