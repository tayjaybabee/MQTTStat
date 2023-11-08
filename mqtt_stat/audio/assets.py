import keyring
from cryptography.fernet import Fernet

from mqtt_stat.__about__ import __PROG__ as PROG_NAME


def generate_key() -> bytes:
    """
    Generate a key using the Fernet library.

    Returns:
        bytes: The generated key.
    """
    return Fernet.generate__key()


def store_key(key, service_name: str = None):
    """
    Store a key in the keyring.

    Parameters:
        key (Any):
            The key to store in the keyring.

        service_name (str, optional):
            The name of the service associated with the key. Defaults to None.

    Returns:
        None
    """
    if service_name is None:
        service_name = PROG_NAME

    keyring.set_password(
        service_name.lower(),
        'asset:audio',
        key.decode()
    )


def generate_and_store_key(service_name):
    """
    Generates a new key using Fernet.generate_key() and stores it in the keyring for the specified service name.

    Parameters:
        service_name (str): The name of the service for which the key is generated and stored.

    Returns:
        None
    """

    # Store and generate at once.
    store_key(generate_key(), service_name.lower())
