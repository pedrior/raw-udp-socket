"""
Projeto de Redes de Computadores: Parte 1 - Cliente UDP
Autores: Davi Luiz, Pedro João e Renan Pascoal
"""

import socket
import threading
import constants as constants   # SERVER_IP, SERVER_PORT, SOCKET_BUFFER_SIZE
import message as message       # pack, unpack
from message import Request
from request import *           # humanize_request
from network_utils import *     # get_source_address
from terminal_utils import *    # clear_screen


def main():
    src_ip, src_port = get_source_address()  # Obtém o endereço IP e porta de origem

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((src_ip, src_port))

    threading.Thread(target=listen_socket, args=(sock,), daemon=True).start()

    while True:
        print(f'Bem-vindo ao cliente UDP! - Enviando de: {src_ip}:{src_port}\n')
        option = int(input('Que tipo requisição deseja solicitar ao servidor?\n\n'
                        '1 - Data e hora\n'
                        '2 - Frase de motivação\n'
                        '3 - Estatísticas do servidor\n'
                        '4 - Sair\n\n'))

        if option < 1 or option > 4:
            print('Opção inválida. Tente novamente.\n')
            clear_screen()
            continue

        if option == 4:
            break

        print()

        # Empacota a mensagem de requisição e a envia
        payload, identifier = message.pack_payload(Request(option - 1))

        print(f'Enviando requisição Nº {identifier}...')
        sock.sendto(payload, (constants.SERVER_IP, constants.SERVER_PORT))

        input()
        clear_screen()

    sock.close()
    exit(0)

def listen_socket(sock: socket.socket):
    while True:
        if not sock: # A thread foi interrompida
            break

        # Recebe a resposta do servidor e a desempacota.
        rcv_payload, _ = sock.recvfrom(constants.SOCKET_BUFFER_SIZE)
        unpacket_payload = message.unpack_payload(rcv_payload)

        if (unpacket_payload == None):
            print('Ocorreu um erro ao processar a sua requisição. Tente novamente!')
        else:
            (request, identifier, data) = unpacket_payload
            print(f'\nRecurso "{humanize_resquest(request)}" solicitado Nº {identifier}: {data}')

        print('\n\nPressione ENTER para continuar...\n')

if __name__ == "__main__":
    main()