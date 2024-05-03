def checksum(data: bytes) -> int:
    sum = 0
    length = len(data)

    # Adiciona um byte de padding (0) se o tamanho dos dados for ímpar
    if (length % 2):
        data += b'\0'
        length += 1

    # Soma os dados em porções de 2 bytes
    for i in range(0, length, 2):
        sum += (data[i] << 8) + (data[i + 1])

    # Faz a soma dos 16 bits mais significativos com os 16 bits menos significativos (wraparound)
    sum = (sum >> 16) + (sum & 0xFFFF)

    # Faz o complemento de 1 da soma e mantém apenas os 16 bits menos significativos
    sum = ~sum & 0xFFFF

    return sum