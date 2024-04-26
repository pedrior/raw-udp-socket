import socket
import constants as constants
import message as message
from message import ResourceType
from resources import *

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def parse_resource_type(option: int) -> int:
    if option == 1:
        return ResourceType.Datetime
    elif option == 2:
        return ResourceType.MotivationQuote
    else:
        return ResourceType.ServerStats


while True:
    print('Bem-vindo ao cliente UDP!\n')
    option = int(input('Digite o tipo do recurso que deseja solicitar ao servidor:\n'
                       '1 - Data e hora\n'
                       '2 - Frase de motivação\n'
                       '3 - Estatísticas do servidor\n'
                       '4 - Sair\n\n'))

    if option < 1 or option > 4:
        print('Opção inválida. Tente novamente.\n')
        continue

    if (option == 4):
        break

    print()

    # Cria uma mensagem de requisição com o tipo de recurso solicitado.
    request = message.pack(parse_resource_type(option))

    # Envia a mensagem de requisição para o servidor.
    try:
        client.sendto(request, (constants.HOST_IP, constants.HOST_PORT))
        pass
    except Exception as e:
        raise e

    # Recebe a resposta do servidor e a desempacota.
    # { 'resource': ResourceType, 'identifier': int, 'data': any }
    response = message.unpack(client.recv(constants.SOCKET_BUFFER_SIZE))

    if (response == None):
        print('Ocorreu um erro ao processar a sua requisição. Tente novamente!\n')
    else:
        identifier = response["identifier"]
        resource = response["resource"]
        data = response["data"]

        print(
            f'\nRecurso "{humanize_resource_type(resource)}" solicitado Nº {identifier}: {data}\n')

    input('\nPressione ENTER para continuar...\n')
    print("\033c", end="")

client.close()
