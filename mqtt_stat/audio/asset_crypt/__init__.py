import keyring
from cryptography.fernet import Fernet

from mqtt_stat.__about__ import __PROG__ as PROG_NAME


class AssetCrypt:
    DEFAULT_SERVICE_NAME = PROG_NAME

    def __init__(
            self,
            asset_path: str,
            service_name: (str | None) = None,
    ):
        """
        Initializes the object with the given asset path and service name.

        Arguments:
            asset_path (str): The path to the asset.
            service_name (str | None, optional): The name of the service. Defaults to None.

        Returns:
            None
        """
        self.__service_name = service_name or self.DEFAULT_SERVICE_NAME
        self.__asset_path = asset_path
        self.__fernet = None

    @property
    def asset_path(self):
        return self.__asset_path

    @property
    def fernet(self):
        return self.__fernet

    @property
    def service_name(self):
        return self.__service_name

    def __enter__(self):
        # Retrieve or generate a key
        key = self.get_key()
        self.__fernet = Fernet(key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_key(self):
        # Retrieve the key from the keyring or generate a new one
        key = keyring.get_password(self.service_name, 'encryption_key')

        if key is None:
            key = Fernet.generate_key()
            keyring.set_password(self.service_name, 'encryption_key', key.decode())

        return key

    def encrypt(self, output_path):
        # Encrypt the asset and write it to the output path
        with open(self.asset_path, 'rb') as file:
            data = file.read()

        encrypted_data = self.fernet.encrypt(data)

        with open(output_path, 'wb') as file:
            file.write(encrypted_data)

    def decrypt(self):
        # Decrypt the asset and return the decrypted data.
        with open(self.asset_path, 'rb') as file:
            encrypted_data = file.read()

        return self.fernet.decrypt(encrypted_data)
