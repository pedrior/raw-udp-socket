"""
Projeto de Redes de Computadores: Parte 2 - Cliente UDP RAW 💪
Autores: Davi Luiz, Pedro João e Renan Pascoal
"""

import sys
import socket
import struct
import threading
import constants as constants    # SERVER_IP, SERVER_PORT, SOCKET_BUFFER_SIZE
import message as message        # pack, unpack
from message import Request
from request import *            # humanize_request
from checksum import *           # checksum
from network_utils import *      # get_source_address
from terminal_utils import *     # clear_screen


def main():
    src_ip, src_port = get_source_address() # Obtém o endereço IP e porta de origem
    dst_ip, dst_port = (constants.SERVER_IP, constants.SERVER_PORT)

    # Cria um socket RAW para enviar a requisição ao servidor. O uso de socket RAW não é mais suportado no Windows,
    # então é necessário utilizar IPPROTO_UDP para enviar pacotes.O protocolo IPPROTO_RAW implica IP_HDRINCL habilitado,
    # o que significa que o cabeçalho IP deve ser construído manualmente (man 7 raw, Linux manual page).
    send_sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_RAW,
        socket.IPPROTO_RAW if 'linux' in sys.platform else socket.IPPROTO_UDP)

    # O recebimento via IPPROTO_RAW não é possível usando socket raw (man 7 raw, Linux manual page), então é necessário
    # criar um novo socket IPPROTO_UDP para receber a resposta do servidor. NOTA: IPPROTO_UDP pode está sendo utilizado
    # se esse código estiver sendo executado em um sistema operacional Windows, fazendo o uso desse socket para recebi-
    # mento desnecessário, mas vamos manter por simplicidade.
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    
    # Conecta o socket de recebimento ao servidor de destino
    recv_sock.connect((dst_ip, dst_port))

    # Inicia uma thread para escutar as respostas do servidor
    threading.Thread(target=listen_socket, args=(recv_sock,), daemon=True).start()

    while True:
        print(f'Bem-vindo ao cliente UDP RAW 💪! - Enviando de: {src_ip}:{src_port}\n')
        option = int(input('Que tipo requisição deseja solicitar ao servidor?\n\n'
                        '1 - Data e hora\n'
                        '2 - Frase de motivação\n'
                        '3 - Estatísticas do servidor\n'
                        '4 - Sair\n\n'))

        if option < 1 or option > 4:
            print('Opção inválida. Tente novamente.\n')
            clear_screen()

            continue

        if (option == 4):
            break

        print()

        # Empacota a mensagem de requisição
        payload, identifier = message.pack_payload(Request(option - 1))

        # Prepara o segmento UDP (UDP Header + Payload)
        segment = build_segment(src_ip, dst_ip, src_port, dst_port, payload)

        print(f'Enviando requisição Nº {identifier}...')
        if ('win32' in sys.platform):
            # O cabeçalho está sendo construído pelo Windows
            send_sock.sendto(segment, (dst_ip, dst_port))
        else:
            # Prepara o datagrama IP (IP Header + Segment)
            datagram = build_datagram(src_ip, dst_ip, segment)
            send_sock.sendto(datagram, (dst_ip, dst_port))

        input()
        clear_screen()
     
    send_sock.close()
    recv_sock.close()
    exit(0)

def listen_socket(recv_sock: socket.socket):
    while True:
        if not recv_sock: # A thread foi interrompida
            break

        datagram, _ = recv_sock.recvfrom(constants.SOCKET_BUFFER_SIZE)
        # Desempacota o datagrama recebido e extrai o conteúdo do payload 
        unpacket_payload = message.unpack_datagram(datagram)

        if (unpacket_payload == None):
            print('Ocorreu um erro ao processar a sua requisição. Tente novamente!')
        else:
            (request, identifier, data) = unpacket_payload
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
