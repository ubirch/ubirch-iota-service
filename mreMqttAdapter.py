import _thread
import argparse
import json
import logging
import signal
import sys
import uuid

from pythonjsonlogger import jsonlogger
import mqtt.client as mqtt

from util import utils

logger = logging.getLogger('mreMqttAdapter')

parser = argparse.ArgumentParser(description='Extend UCS mailing lists')
parser.add_argument('-sids', '--sourcedeviceids', help="list of devicIds (; = seperator)", metavar="DEVICEIDS",
                    required=True)
parser.add_argument('-sh', '--sourcehost', help="host of source mqtt server", metavar="HOST", required=True)
parser.add_argument('-sp', '--sourceport', help="port of source mqtt server", metavar="PORT", type=int, default=1883)
parser.add_argument('-sus', '--sourceuser', help="user of source mqtt server", metavar="USER", default=None)
parser.add_argument('-spw', '--sourcepassword', help="password of source mqtt server", metavar="PASSWORD", default=None)
parser.add_argument('-sc', '--sourcecrt', help="TLS certificate of source mqtt server", metavar="CRT", default=None)

parser.add_argument('-tt', '--targettopic', help="subscribed topic to write to", metavar="TOPIC", required=True)
parser.add_argument('-th', '--targethost', help="host of target mqtt server", metavar="HOST", required=True)
parser.add_argument('-tp', '--targetport', help="port of target mqtt server", metavar="PORT", type=int, default=1883)
parser.add_argument('-tus', '--targetuser', help="user of target mqtt server", metavar="USER", default=None)
parser.add_argument('-tpw', '--targetpassword', help="password of target mqtt server", metavar="PASSWORD", default=None)
parser.add_argument('-tc', '--targetcrt', help="TLS certificate of target mqtt server", metavar="CRT", default=None)

parser.add_argument('-ljs', '--logjson', help="json based logs", metavar="JSLOG", type=bool, default=False)

parser.add_argument('-eid', '--envid', help="enviroment id", metavar="ENVID", default="local-dev")

parser.add_argument('-ll', '--loglevel', help="log level", metavar="LOGLEVEL", default="DEBUG")

args = parser.parse_args()

log_level = utils.log_level(args.loglevel)
logger.setLevel(log_level)

log_keys = [
    'asctime',
    'created',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'thread',
    'threadName'
]

if args.logjson:
    logHandler = logging.StreamHandler()
    log_format = lambda x: ['%({0:s})'.format(i) for i in x]
    custom_format = ' '.join(log_format(log_keys))
    formatter = jsonlogger.JsonFormatter(custom_format)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    logging.basicConfig(format=FORMAT)


sDeviceId = args.sourcedeviceids.split(";")
sHost = args.sourcehost
sPort = args.sourceport
sUser = args.sourceuser
sPwd = args.sourcepassword
sCrt = args.sourcecrt

tTopic = args.targettopic
tHost = args.targethost
tPort = args.targetport
tUser = args.targetuser
tPwd = args.targetpassword
tCrt = args.targetcrt

envId = args.envid

logger.info("mreMqttAdaper started")

def on_connect(client, userdata, flags, rc):
    logger.debug("Connected as {} with result code {}".format(client._client_id, rc))
    deviceId = userdata
    sTopic = "{}/ubirch/devices/{}/processed".format(envId, deviceId)
    logger.info("subscribe to {}".format(sTopic))
    client.subscribe(sTopic)


def on_disconnect(client, userdata, rc):
    logger.debug("Disconnected ClientId{} with result code {}".format(client._client_id, rc))


def on_message(client, userdata, msg):
    logger.debug("{}  // {}".format(msg.topic, msg.payload))
    try:
        jDoc = json.loads(msg.payload)
        rawDoc = jDoc['deviceDataRaw']
        payload = json.dumps(rawDoc)
        logger.debug("use topic: {}".format(tTopic))
        logger.debug("out message: {}".format(payload))
        connectToTarget().publish(topic=tTopic, payload=payload)
    except:
        logger.error("invalid json: {}".format(msg.payload))


def connectToSource(deviceId):
    logger.info("connect to source MQTT for device {}".format(deviceId))
    clientId = "ubirch/{}".format(deviceId)
    sClient = mqtt.Client(client_id=clientId)
    sClient.on_connect = on_connect
    sClient.on_disconnect = on_disconnect
    sClient.on_message = on_message
    sClient.user_data_set(deviceId)
    if sUser is not None and sPwd is not None:
        sClient.username_pw_set(sUser, sPwd)
    sClient.connect(
        sHost, sPort, 30
    )
    sClient.loop_forever()


def connectToTarget():
    logger.info("connect to target MQTT")
    tclient = mqtt.Client(client_id="mre/{}".format(uuid.uuid4()))
    tclient.on_connect = on_connect
    tclient.on_disconnect = on_disconnect

    if tCrt is not None:
        tclient.tls_set(ca_certs=tCrt)
    if tUser is not None and tPwd is not None:
        tclient.username_pw_set(tUser, tPwd)

    tclient.connect(
        tHost, tPort, 60
    )
    return tclient


if len(sDeviceId) > 0:

    for did in sDeviceId:
        _thread.start_new_thread(connectToSource, (did,))
else:
    logger.error("invalid source deviceIds: {}".format(sDeviceId))


def signal_handler(signal, frame):
    logger.info('You pressed Ctrl+C!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
logger.info('Press Ctrl+C')
signal.pause()
