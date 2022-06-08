import json
import os

WINDOW_WIDTH, WINDOW_HEIGHT = 400, 200
TIMEOUT = 5


def open_environment() -> dict:
    """
    Open the environment file and return the data.
    """
    with open(os.path.join(os.path.dirname(__file__), '..', 'environment.json')) as f:
        return json.load(f)


def get_fernet_key() -> bytes:
    """
    Get the fernet key from the environment file.
    """
    return bytes(open_environment()['Key'], 'utf-8')


if __name__ == '__main__':
    print(open_environment()['Version'])
