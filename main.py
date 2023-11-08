from mqtt_stat import MQTTClient
from mqtt_stat.config import config


def main(broker=None, port=None, topic=None, reply_topic=None, birth_topic=None, lwt_topic=None):
    broker = broker or config['mqtt_broker']
    port = port or config['mqtt_port']
    topic = topic or config['system_status_topic']
    reply_topic = reply_topic or config['reply_topic']
    birth_topic = birth_topic or config['birth_topic']
    lwt_topic = lwt_topic or config['lwt_topic']

    client = MQTTClient(broker, port, topic, reply_topic, birth_topic, lwt_topic)
    client.run()
