import random
from resources import *

def pack(resource: ResourceType) -> bytes:
    identifier = random.randint(1, 65535)

    # A mensagem de requisição é composta por 3 bytes, sendo o primeiro byte contendo o tipo da mensagem e o recurso
    # solicitado, o segundo e terceiro bytes contendo o identificador da requisição.
    message = bytearray()

    message.append(resource.value)

    # Escreve o identificador nos 2 bytes seguintes, sendo o primeiro byte os 8 bits mais significativos e o segundo
    # byte os 8 bits menos significativos do identificador
    message.append((identifier & 0xFF00) >> 8)
    message.append(identifier & 0xFF)

    return bytes(message)


def unpack(bytes: bytes) -> dict:
    resource = (bytes[0] & 0x0F)            # 4 bits menos significativos do byte 1: Tipo do recurso
    identifier = (bytes[1] << 8) | bytes[2] # Byte 1 e 2: Identificador da requisição
    size = bytes[3]                         # Byte 3: Tamanho da resposta
    data = bytes[4:]                        # Byte 4 em diante: Dados da resposta

    # Verifica se o servidor está informando um erro
    if (resource == RES_INVALID or size == 0):
        return None

    # Converte o conteúdo da resposta para o tipo de dado correto
    if (resource == ResourceType.ServerStats.value):
        data = int.from_bytes(data, byteorder='big')
    else:
        data = data.decode('UTF-8', 'ignore')

    return {
        'resource': ResourceType(resource),
        'identifier': identifier,
        'data': data
    }
