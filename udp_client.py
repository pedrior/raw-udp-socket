import socket
import constants as constants
import message as message
from message import ResourceType
from resources import *

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
    print('Bem-vindo ao cliente UDP!\n')
    option = int(input('Digite o tipo do recurso que deseja solicitar ao servidor:\n'
                       '0 - Data e hora\n'
                       '1 - Frase de motivação\n'
                       '2 - Estatísticas do servidor\n'
                       '3 - Sair\n\n'))

    if option < 0 or option > 3:
        print('Opção inválida. Tente novamente.\n')
        continue

    if (option == 3):
        break

    print()

    # Cria uma mensagem de requisição com o tipo de recurso solicitado.
    request = message.pack(ResourceType(option))

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
