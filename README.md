# Projeto de Redes: RAW UDP Socket 

Implemente dois clientes (um utilizando socket UDP e outro utilizando socket RAW) de uma
aplicação do tipo cliente/servidor que encaminha requisições para o servidor que está executando através
dos protocolos UDP/IP no endereço IP 15.228.191.109 e porta 50000. Cada cliente deve solicitar ao
usuário a escolha de um dos tipos de requisição abaixo:
1. Data e hora atual;
2. Uma mensagem motivacional para o fim do semestre;
3. A quantidade de respostas emitidas pelo servidor até o momento.
4. Sair.

Uma vez que o usuário tenha feito a sua escolha, o cliente deve encaminhar uma requisição
devidamente formatada para o servidor, de acordo com o formato de mensagem especificado abaixo. O
servidor por sua vez emitirá uma resposta de volta para o cliente utilizando o mesmo formato de
mensagem. Em seguida o cliente deverá exibir a resposta recebida pelo servidor de uma forma adequada
para a legibilidade pelo usuário final. Por fim, o programa cliente deverá aguardar novas requisições do
cliente até que o usuário selecione a opção “Sair”.

## FORMATO DAS MENSAGENS DE REQUISIÇÃO/RESPOSTA

| 4 bits  | 4 bits |    16 bits    |     8 bits    |    N bits   |
|---------|--------|---------------|---------------|-------------|
| req/res |  tipo  | identificador | Tamanho (res) |   Resposta  |

- __req/res__: indicação para mensagem do tipo requisição (bits 0000) ou resposta (bits 0001);
  
- __tipo__: indicação do tipo de requisição ou resposta. Bits 0000 para solicitação de data, bits
0001 para solicitação de frase motivacional para o fim do semestre e bits 0010 para
quantidade de respostas emitidas pelo servidor. O servidor ainda pode emitir uma resposta
com o tipo 0011 para indicar que recebeu uma requisição inválida do cliente;

- __identificador__: número não negativo de 2 bytes determinado pelo cliente. O cliente deve
sortear um número entre 1 e 65535 toda vez que for enviar uma nova requisição para o
servidor. O identificador 0 é reservado para o servidor informar o recebimento de uma
requisição inválida;

- __tamanho (res)__: campo utilizado apenas em respostas geradas pelo servidor. Indica
o tamanho da resposta propriamente ditas, em número de bytes (1 a 255). O tamanho 0 é
reservado para quando o servidor envia uma resposta indicando o recebimento de uma
requisição inválida;

- __resposta__: uma sequência de bytes contendo a resposta
solicitada pelo usuário. Caso o servidor esteja informando o recebimento de uma
requisição inválida, nenhum byte é encaminhado neste campo.
