import socket
import os
import struct
import random
import sys
from typing import Tuple

# Formatação do pacote header IP: (version, IHL, type of service, total length, identification, flags, fragment offset, TTL, protocol, checksum, source IP, destination IP)
IP_HEADER_FORMAT = '!BBHHHBBH4s4s'

# Formatação do pacote do header UDP: (source port, destination port, length, checksum)
UDP_HEADER_FORMAT = '!HHHH'

# Função para calcular o checksum para os headers
def calculate_checksum(msg: bytes) -> int:
    s = 0

    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + (msg[i+1] if i+1 < len(msg) else 0)
        s = s + w

    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 16)

    s = ~s & 0xffff

    return s

# Função para construir o IP header
def construct_ip_header(source_ip: str, dest_ip: str, placeholder: int, protocol: int, udp_length: int) -> bytes:
    # Random packet identification
    packet_id = random.randint(1, 65535)

    # Criando o IP header
    ip_header = struct.pack(IP_HEADER_FORMAT, 
                            69,  # Version e IHL
                            0,   # Tipo de Serviço
                            20 + udp_length,  # Tamanho total (IP header + UDP header + Data)
                            packet_id,  # Identificação
                            0,   # Flags e Fragment Offset
                            64,  # TTL - time to live
                            protocol,  # Protocolo
                            0,   # Checksum 
                            socket.inet_aton(source_ip),  # Source IP
                            socket.inet_aton(dest_ip)  # Destination IP
                           )

    # Calculando o checksum correto
    checksum = calculate_checksum(ip_header)
    ip_header = struct.pack(IP_HEADER_FORMAT, 
                            69, 
                            0, 
                            20 + udp_length, 
                            packet_id, 
                            0, 
                            64, 
                            protocol, 
                            checksum, 
                            socket.inet_aton(source_ip), 
                            socket.inet_aton(dest_ip)
                           )
    
    return ip_header

# Função para construir o header UDP
def construct_udp_header(source_port: int, dest_port: int, length: int, checksum: int) -> bytes:
    udp_header = struct.pack(UDP_HEADER_FORMAT, source_port, dest_port, length, checksum)
    return udp_header

# Função para construir o pacote
def construct_packet(request_type: int, identifier: int, server_ip: str, server_port: int) -> bytes:
    request_header = (0 << 4) | request_type
    request = struct.pack('!BH', request_header, identifier)
    
    udp_length = 8 + len(request) 
    
    source_ip = '127.0.0.1'  
    dest_ip = server_ip
    ip_header = construct_ip_header(source_ip, dest_ip, 0, socket.IPPROTO_UDP, udp_length)
    udp_header = construct_udp_header(0, server_port, udp_length, 0)   
    packet = ip_header + udp_header + request

    return packet

def send_and_receive(sock, server_ip, server_port, packet):
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    
    # Enviar o pacote ao servidor
    sock.sendto(packet, (server_ip, server_port))

    # Recebendo a resposta do servidor
    response, addr = sock.recvfrom(1024)  # Buffer size de 1024 bytes

    return response

# função para extrair os dados recebidos do servidor
def parse_response(response):
    ip_header = response[0:20]
    udp_header = response[20:28]
    message = response[28:]

    iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
    udph = struct.unpack('!HHHH', udp_header)

    message_header = message[:3]
    message_data = message[3:]

    res, identifier = struct.unpack('!BH', message_header)

    response_type = res & 0x0F  

    response_message = message_data.decode()

    if response_type == 0x0:  # Data e Hora
        print(f"Data e Hora: {response_message}")
    elif response_type == 0x1:  # Frase motivacional
        print(f"Frase motivacional: {response_message}")
    elif response_type == 0x2:  # Número de respostas emitidas
        response_count = struct.unpack('!I', message_data)[0]
        print(f"Número de respostas emitidas pelo servidor: {response_count}")
    elif response_type == 0x3:  # Requisição inválida
        print(f"Recebemos uma requisição inválida do servidor.")
    else:
        print(f"Tipo de resposta não reconhecido: {response_type}")
        
def client_main():
    server_ip = '15.228.191.109'
    server_port = 50000
    running = True

    # Criando um novo socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error as msg:
        print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    while running:
        # Solicitar a escolha do usuário
        print("Escolha um tipo de requisição:")
        print("1. Data e hora atual")
        print("2. Uma mensagem motivacional para o fim do semestre")
        print("3. A quantidade de respostas emitidas pelo servidor até o momento")
        print("4. Sair")

        choice = input("Digite sua opção (1-4): ")

        if choice == '4':
            running = False
            print("Saindo...")
            continue

        # Gerar um identificador aleatório para a requisição
        identifier = random.randint(1, 65535)

        # Construir o pacote de requisição baseado na escolha do usuário
        request_type = int(choice) - 1
        request_packet = construct_packet(request_type, identifier, server_ip, server_port)

        # Enviar a requisição e receber a resposta do servidor
        response = send_and_receive(sock, server_ip, server_port, request_packet)

        # Analisar a resposta e exibir para o usuário
        parse_response(response)

    # Encerrar o socket
    sock.close()

if __name__ == "__main__":
    client_main()