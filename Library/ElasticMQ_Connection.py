#Librabry used in sender and receiver scripts to connect to the elasticMQ Server

# TO START THE SERVER
#  See custom.conf for more details

# java -Dconfig.file=custom.conf -jar elasticmq-server-0.14.2.jar

import boto3

url = 'http://localhost:9324'


def connect(url):
    client = boto3.resource('sqs',
                        endpoint_url=url,  #
                        region_name="elasticmq",  #
                        aws_secret_access_key='x',  # parameters passed as arguments
                        aws_access_key_id='x',  #
                        use_ssl=False)
    return client

import argparse

# def connect(endpoint_url, region_name, aws_secret_access_key, aws_access_key_id):
#     client = boto3.resource('sqs',
#                         endpoint_url=url,  #
#                         region_name="elasticmq",  #
#                         aws_secret_access_key='x',  # parameters passed as arguments
#                         aws_access_key_id='x',  #
#                         use_ssl=False)
#     return client

#arguments here

# parser = argparse.ArgumentParser(description='Extend UCS mailing lists')
# parser.add_argument('-sids', '--sourcedeviceids', help="list of devicIds (; = seperator)", metavar="DEVICEIDS",
#                     required=True)
# parser.add_argument('-sh', '--sourcehost', help="host of source mqtt server", metavar="HOST", required=True)
# parser.add_argument('-sp', '--sourceport', help="port of source mqtt server", metavar="PORT", type=int, default=1883)
# parser.add_argument('-sus', '--sourceuser', help="user of source mqtt server", metavar="USER", default=None)
#
#args = parser.parse_args()




#client = connect(endpoint_url, region_name, aws_secret_access_key, aws_access_key_id)

def getQueue(queue_name):
    client = connect(url)
    queue = client.get_queue_by_name(QueueName=queue_name)
    print('The url of the queue is : ' + queue.url)
    return queue
