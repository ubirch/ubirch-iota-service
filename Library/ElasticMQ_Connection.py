# import subprocess

# bashCommand = "cd ../elasticMQServer && java -Dconfig.file=custom.conf -Dlogback.configurationFile=my_logback.xml -jar elasticmq-server-0.14.2.jar"
# process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
# output, error = process.communicate()

#Librabry used in sender and receiver scripts to connect to the elasticMQ Server

# TO START THE SERVER
# java -Dconfig.file=custom.conf -jar elasticmq-server-0.14.2.jar


import boto3


def connect(url):
    client = boto3.resource('sqs',
                            endpoint_url='%s' % (url), #
                            region_name="elasticmq", #
                            aws_secret_access_key='x', #parameters
                            aws_access_key_id='x', #
                            use_ssl=False)
    return client


def getQueue(url, queue_name):
    client = connect(url)
    queue = client.get_queue_by_name(QueueName=queue_name)
    print('The url of the queue is : ' + queue.url)
    return queue
