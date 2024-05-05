"""
Projeto de Redes de Computadores: Parte 2 - Cliente UDP RAW 💪
Autores: Davi Luiz, Pedro João e Renan Pascoal
"""

import logging
import sys
import socket
import struct
import threading
import constants as constants    # SERVER_IP, SERVER_PORT, SOCKET_BUFFER_SIZE
import message as message        # make_payload, unpack_payload_dgram
from message import Request
from request import *            # humanize_request
from checksum import *           # checksum
from network_utils import *      # get_source_address
from terminal_utils import *     # clear_screen


def main():
    is_linux = False

    # Obtém o endereço IP da interface de rede e uma porta aleatória
    src_ip, src_port = get_source_address()
    dst_ip, dst_port = (constants.SERVER_IP, constants.SERVER_PORT)

    # Cria um Socket RAW para enviar requisições ao servidor. No Linux, usamos o protocolo IPPROTO_RAW para enviar
    # datagramas IP, neste cenário, o cabeçalho IP é construído manualmente. Nos demais SO, o protocolo IPPROTO_RAW 
    # não é suportado, então usamos o protocolo IPPROTO_UDP para enviar segmentos, o que significa que o cabeçalho IP 
    # é construído pelo sistema operacional. Além disso, o recebimento via protocolo RAW não é possível no linux
    # (man raw 7), fazendo necessário criar um novo Socket RAW de protocolo UDP para receber as respostas do servidor.
    try:
        send_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_RAW,
            socket.IPPROTO_RAW if is_linux else socket.IPPROTO_UDP)
    except Exception as e:
        logging.error(f'Falha ao criar o socket de envio: {e}')
        exit(1)

    # Cria um novo socket raw de protocolo IPPROTO_UDP e inicia uma thread para processar as respostas do servidor.
    # A criação de um novo Socket para recebimento é necessário apenas quando usamos protocolo IPPROTO_RAW, no entanto,
    # para facilitar a implementação, criamos um novo Socket para receber as respostas do servidor independente do SO.
    try:
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        recv_sock.connect((dst_ip, dst_port))
    except Exception as e:
        logging.error(f'Falha ao criar o socket de recebimento e conectar ao servidor: {e}')
        exit(1)

    threading.Thread(target=process_responses, args=(recv_sock,), daemon=True).start()

    while True:
        print(f'Bem-vindo ao cliente UDP RAW 💪! - Enviando de: {src_ip}:{src_port} no {sys.platform}\n')
        option = int(input('Que tipo requisição deseja solicitar ao servidor?\n\n'
                        '1 - Data e hora\n'
                        '2 - Frase de motivação\n'
                        '3 - Estatísticas do servidor\n'
                        '4 - Sair\n\n'))

        if option < 1 or option > 4:
            clear_screen()
            continue

        if (option == 4):
            break

        print()

        # Empacota a mensagem de requisição
        payload, identifier = message.make_payload(Request(option - 1))

        # Prepara o segmento UDP (UDP Header + Payload)
        segment = build_segment(src_ip, dst_ip, src_port, dst_port, payload)

        print(f'Enviando requisição Nº {identifier}...')

        # Envia o datagrama IP (Linux com IPPROTO_RAW) ou o segmento UDP (demais SO com IPPROTO_UDP)
        try:
            if is_linux:
                # Prepara o datagrama IP (IP Header + Segment)
                datagram = build_datagram(src_ip, dst_ip, segment)
                send_sock.sendto(datagram, (dst_ip, dst_port))
            else:
                send_sock.sendto(segment, (dst_ip, dst_port))
        except Exception as e:
            logging.error(f'Falha ao enviar a requisição: {e}')
            break

        input()
        clear_screen()
     
    send_sock.close()
    recv_sock.close()
        
    exit(0)

def process_responses(recv_sock: socket.socket):
    while True:
        if not recv_sock: # A thread foi interrompida
            break

        # Recebe a resposta do servidor e desempacota o payload
        try:
            datagram = recv_sock.recvfrom(constants.SOCKET_BUFFER_SIZE)[0]
        except Exception as e:
            logging.error(f'Falha ao receber a resposta: {e}')
            print('\n\nPressione ENTER para continuar...\n')
            break

        payload = message.unpack_payload_dgram(datagram)
        if (payload == None):
            print('Ocorreu um erro ao processar a sua requisição. Tente novamente!')
        else:
            (request, identifier, data) = payload
            print(f'\nRecurso "{humanize_resquest(request)}" solicitado Nº {identifier}: {data}')

        print('\n\nPressione ENTER para continuar...\n')

def build_segment(src_ip: str, dst_ip: str, src_port: int, dst_port: int, payload: bytes) -> bytes:
    udp_zero = 0
    udp_checksum = 0
    udp_protocol = socket.IPPROTO_UDP
    udp_length = 8 + len(payload)

    # Cria o pseudo-cabeçalho UDP para cálculo do checksum. Quando o UDP é executado sobre o IPv4, o checksum é
    # calculado sobre um pseudo-cabeçalho que contém algumas mesmas informações do cabeçalho IP.
    udp_pseudo_header = struct.pack('!4s4sBBH',
                                    socket.inet_aton(src_ip),
                                    socket.inet_aton(dst_ip),
                                    udp_zero,
                                    udp_protocol,
                                    udp_length)

    # Cria o cabeçalho UDP
    udp_header = struct.pack('!4H', src_port, dst_port, udp_length, udp_checksum)

    # Calcula o checksum do cabeçalho UDP (incluindo o pseudo-cabeçalho) e dos dados (payload)
    udp_checksum = checksum(udp_pseudo_header + udp_header + payload)

    # Recria o cabeçalho UDP com o checksum calculado
    udp_header = struct.pack('!4H', src_port, dst_port, udp_length, udp_checksum)

    return udp_header + payload

def build_datagram(src_ip: str, dst_ip: str, segment: bytes) -> bytes:
    ip_ihl = 5                           # Internet Header Length
    ip_ver = 4                           # IPv4
    ip_tos = 0                           # Type of Service
    ip_tot_len = 20                      # Total Length (O kernel irá recalcular)
    ip_id = 54321                        # Identification
    ip_frag_off = 0                      # Fragment Offset
    ip_ttl = 255                         # Time to Live
    ip_proto = socket.IPPROTO_UDP        # Protocolo UDP
    ip_check = 0                         # Checksum (O kernel irá recalcular)
    ip_src_ip = socket.inet_aton(src_ip) # Source IP
    ip_dst_ip = socket.inet_aton(dst_ip) # Destination IP

    # Cria o cabeçalho IP
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            (ip_ver << 4) + ip_ihl,
                            ip_tos,
                            ip_tot_len,
                            ip_id,
                            ip_frag_off,
                            ip_ttl,
                            ip_proto,
                            ip_check,
                            ip_src_ip,
                            ip_dst_ip)

    return ip_header + segment

if __name__ == '__main__':
    main()
