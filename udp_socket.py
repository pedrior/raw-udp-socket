"""
Projeto de Redes de Computadores: Parte 1 - Cliente UDP
Autores: Davi Luiz, Pedro João e Renan Pascoal
"""

import logging
import socket
import threading
import constants as constants   # SERVER_IP, SERVER_PORT, SOCKET_BUFFER_SIZE
import message as message       # make_payload, unpack_payload
from message import Request
from request import *           # humanize_request
from network_utils import *     # get_source_address
from terminal_utils import *    # clear_screen


def main():
    # Obtém o endereço IP da interface de rede e uma porta aleatória
    src_ip, src_port = get_source_address()
    dst_ip, dst_port = (constants.SERVER_IP, constants.SERVER_PORT)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((dst_ip, dst_port))
    except Exception as e:
        logging.error(f'Falha ao criar o socket: {e}')
        exit(1)

    # Inicia uma thread para processar as respostas do servidor
    threading.Thread(target=process_responses, args=(sock,), daemon=True).start()

    while True:
        print(f'Bem-vindo ao cliente UDP! - Enviando de: {src_ip}:{src_port}\n')
        option = int(input('Que tipo requisição deseja solicitar ao servidor?\n\n'
                        '1 - Data e hora\n'
                        '2 - Frase de motivação\n'
                        '3 - Estatísticas do servidor\n'
                        '4 - Sair\n\n'))

        if option < 1 or option > 4:
            clear_screen()
            continue

        if option == 4:
            break

        print()

        # Cria uma mensagem de requisição e a envia
        payload, identifier = message.make_payload(Request(option - 1))

        print(f'Enviando requisição Nº {identifier}...')

        try:
            sock.sendto(payload, (dst_ip, dst_port))
        except Exception as e:
            logging.error(f'Falha ao enviar a requisição: {e}')
            break

        input()
        clear_screen()

    sock.close()
    exit(0)

def process_responses(recv_sock: socket.socket):
    while True:
        if not recv_sock: # A thread foi interrompida
            break

        # Recebe a resposta do servidor e desempacota o payload
        try:
            payload = recv_sock.recvfrom(constants.SOCKET_BUFFER_SIZE)[0]
        except Exception as e:
            logging.error(f'Falha ao receber a resposta: {e}')
            print('\n\nPressione ENTER para continuar...\n')
            break
        
        payload = message.unpack_payload(payload)
        if (payload == None):
            print('Ocorreu um erro ao processar a sua requisição. Tente novamente!')
        else:
            (request, identifier, data) = payload
            print(f'\nRecurso "{humanize_resquest(request)}" solicitado Nº {identifier}: {data}')

        print('\n\nPressione ENTER para continuar...\n')

if __name__ == "__main__":
    main()