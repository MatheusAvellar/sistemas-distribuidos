# Ativo (adaptado da Aula 4 de Sistemas Distribuídos)

import socket

HOST = "localhost"
PORT = 5000

# Abrir socket pela internet, usando TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta-se ao host e porta definidos pelas constantes
sock.connect((HOST, PORT))

# Loop infinito para enviar N mensagens
while True:
  # Recebe input do usuário
  mensagem_customizada = input()

  # Se input for código especial, encerra a conexão
  if mensagem_customizada == "SD":
    print("Código especial recebido; encerrando conexão")
    break

  # Senão, envia input para o lado 'passivo'
  sock.send(str.encode(mensagem_customizada))

  # Espera resposta do lado 'passivo'
  # Argumento indica tamanho máximo, em bytes, a ser lido
  msg = sock.recv(1024)

  print("Recebeu mensagem: '" + str(msg, encoding="utf-8") + "'")

# Fecha a conexão
sock.close()