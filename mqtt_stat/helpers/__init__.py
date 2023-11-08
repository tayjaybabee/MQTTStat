from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mqtt_stat import MQTTClient


class MQTTPublisher:
    def __init__(self, client, main_topic):
        self.__client = client

    @property
    def client(self) -> 'MQTTClient':
        return self.__client

    @client.setter
    def client(self, new):
        if not isinstance(new, MQTTClient):
            raise TypeError('"client" must be of type "MQTTClient"')
        self.__client = new
