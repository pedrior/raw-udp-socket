import socket
import random


def get_source_address(port: int = None):
    # Usa uma porta aleatória se nenhuma for especificada
    if (port == None):
        port = random.randint(49152, 65535)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 80))
        return (sock.getsockname()[0], port)
