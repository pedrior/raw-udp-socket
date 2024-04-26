import random
from resources import *

MSG_REQUEST = 0b0000
MSG_RESPONSE = 0b0001


def pack(resource: ResourceType) -> bytes:
    identifier = random.randint(1, 65535)

    # A mensagem de requisição é composta por 32 bits, sendo os 4 bits mais significativos o tipo da mensagem, os
    # 4 bits seguintes o tipo do recurso solicitado, os 16 bits seguintes o id da requisição e os 8 bits seguintes
    # reservados para o tamanho da resposta (gerado pelo servidor). Na resposta, os bits após o tamanho da resposta
    # são reservados para o conteúdo da resposta.

    # Escreve os 4 bits mais significativos com o tipo da mensagem
    message = MSG_REQUEST << 28
    # Escreve os 4 bits seguintes com o tipo do recurso solicitado
    message |= resource.value << 24
    # Escreve os 16 bits seguintes com o id da requisição
    message |= identifier << 8

    return message.to_bytes(4, byteorder='big')


def unpack(bytes: bytes) -> dict:

    # Lê os 4 bits mais significativos para obter o tipo da mensagem
    type = (bytes[0] & 0xF0) >> 4

    # Lê os 4 bits seguintes para obter o tipo do recurso solicitado
    resource = (bytes[0] & 0x0F)

    # Se por algum motivo o tipo da mensagem não for uma resposta ou o recurso solicitado
    # for inválido, retorna None
    if (type != MSG_RESPONSE or resource == RES_INVALID):
        return None

    # Lê os 16 bits seguintes para obter o id da requisição
    identifier = (bytes[1] << 8) | bytes[2]

    # Lê os 8 bits seguintes para obter o tamanho da resposta
    response_size = bytes[3]

    # Lê os bits restantes para obter o conteúdo da resposta
    data = bytes[4:4+response_size]

    # Converte o conteúdo da resposta para o tipo de dado correto
    if (resource == ResourceType.ServerStats.value):
        data = int.from_bytes(data, byteorder='big')
    else:
        data = data.decode('ISO-8859-1', 'ignore')

    return {
        'resource': ResourceType(resource),
        'identifier': identifier,
        'data': data
    }
