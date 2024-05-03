import random
from request import *


def pack_payload(request: Request) -> bytes:
    # Formato da mensagem de requisição:
    # ----------------------------------------
    # |  4 bits   | 4 bits  |    16 bits    |
    # |    Req    | Recurso | Identificador |
    # ----------------------------------------

    identifier = random.randint(1, 65535)

    # Escreve o tipo da requisição nos 4 bits menos significativos do byte 1
    byte1 = (0x0 << 4) | request.value

    # Escreve o identificador nos 2 bytes seguintes, sendo o primeiro byte os 8 bits mais significativos e o segundo
    # byte os 8 bits menos significativos do identificador
    byte2 = (identifier & 0xFF00) >> 8
    byte3 = identifier & 0xFF

    payload = (byte1 << 24) | (byte2 << 16) | (byte3 << 8)
    return (payload.to_bytes(4, byteorder='big'), identifier)

def unpack_datagram(datagram: bytes) -> tuple:
    # Extrai o payload do datagrama, ignorando os 20 bytes do cabeçalho IP e os 8 bytes do cabeçalho UDP
    return unpack_payload(datagram[20 + 8:])

def unpack_payload(payload: bytes) -> tuple:
    # Formato da mensagem de resposta:
    # ---------------------------------------------------------
    # |  4 bits  | 4 bits  |    16 bits    | 8 bits  | n bits |
    # |    Res   | Recurso | Identificador | Tamanho |  Dados |
    # ---------------------------------------------------------

    request = (payload[0] & 0x0F)               # 4 bits menos significativos do byte 0: Tipo de requisição
    identifier = (payload[1] << 8) | payload[2] # Byte 1 e 2: Identificador da requisição
    size = payload[3]                           # Byte 3: Tamanho da resposta
    data = payload[4:]                          # Byte 4 em diante: Dados da resposta

    # Verifica se o servidor está informando um erro
    if (request == 0x3 or identifier == 0x0 or size == 0x0):
        return None

    # Interpreta o conteúdo da resposta. Se a requisição for de estatísticas do servidor, os dados são um inteiro,
    # para as demais requisições, os dados são uma string, neste caso a decoficamos para UTF-8
    request = Request(request)
    if (request == Request.ServerStats):
        data = int.from_bytes(data, byteorder='big')
    else:
        data = data.decode('UTF-8', 'ignore')

    return (request, identifier, data)