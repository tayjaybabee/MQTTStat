import json

from paho.mqtt import client as mqtt

from mqtt_stat.audio import start_alarm
from mqtt_stat.shared import MQTTClient
from mqtt_stat.stats.battery import get_battery_info
from mqtt_stat.stats.network import get_network_name


class MQTTClient(MQTTClient):
    def __init__(
            self,
            broker: str,
            port: int,
            listen_topic: str,
            reply_topic: str,
            birth_topic: str,
            lwt_topic: str
    ):
        """
        Initializes the MQTTClient.

        Args:
            broker (str): The broker's URL.
            port (int): The port number to connect to.
            listen_topic (str): The MQTT topic to subscribe to for listening to messages.
            reply_topic (str): The MQTT topic to publish the reply message.
            birth_topic (str): The MQTT topic to publish the birth message.
            lwt_topic (str): The MQTT topic for the broker to publish the LWT message.

        Usage example:
            client = MQTTClient('mqtt.example.com', 1883, 'sensors/temperature', 'sensors/response', 'client/birth', 'client/lwt')
            client.run()
        """
        self.broker = broker
        self.port = port
        self.listen_topic = listen_topic
        self.reply_topic = reply_topic
        self.birth_topic = birth_topic
        self.lwt_topic = lwt_topic
        self.client = mqtt.Client()

        # Configure LWT (Last Will and Testament)
        self.client.will_set(self.lwt_topic, payload=json.dumps({'status': 'offline'}), qos=1, retain=True)

        # Set up the on_connect and on_message event handlers
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def execute_command(self, command, data):
        """
        Executes a command received from the MQTT broker.

        Args:
            command (str):
                The command to execute.
        :
            data (dict):
                The additional data needed for command execution.

        Example::
            >>> client.execute_command('find')

        """
        commands = {
            'get_status': self.get_status,
            'find': self.find_service
        }

        if command in commands:
            commands[command](**data)
        else:
            print(f'Unrecognized command: {command}')

    def find_service(self):
        """
        Plays a sound continuously until the 'Enter' key is pressed.
        """
        start_alarm(interval=1.5, volume_increment=0.05, volume_start=0.05, )

    def get_status(self):
        battery_info = get_battery_info()
        batt_level = battery_info['percent']
        batt_charging = battery_info['power_plugged']
        response = {
            'status': 'responded',
            'network_ssid': get_network_name(),
            'battery_level': batt_level,
            'battery_charging': batt_charging
        }

        self.publish(response)
        print("Sent response message")

    def on_connect(self, client, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response from the server.
        """
        # Truncated for brevity, see previous code for full docstring
        if rc == 0:
            print("Connected to MQTT Broker!")

            # Publish the birth message
            self.client.publish(self.birth_topic, json.dumps({'status': 'online'}), qos=1, retain=True)

            # Subscribe to the listen topic.
            client.subscribe(self.listen_topic)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        """
        The callback for when a PUBLISH message is received from the server.
        """
        print(f"Received message on topic {msg.topic} with payload {msg.payload}")

        # Check if the received message has the payload we are looking for
        try:
            payload = json.loads(msg.payload)
            if payload.get('status') == 'needed':
                self.respond_to_needed_status()


            elif payload.get('status') == 'alert':
                chime.info()
                response = {'status': 'alerted', 'alert_type': 'info'}
                self.client.publish(self.reply_topic, json.dumps(response), qos=1)
                print('Sent reply message.')

        except json.JSONDecodeError:
            print("Invalid payload received, not a JSON")

    def publish(self, data):
        self.client.publish(self.reply_topic, json.dumps(data), qos=1)

        def run(self):
            """
            Starts the MQTT client by connecting to the broker and entering the loop to process network events.
            """

        # Truncated for brevity, see previous code for full docstring
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()
