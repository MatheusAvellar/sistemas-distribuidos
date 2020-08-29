# Passivo (adaptado da Aula 4 de Sistemas Distribuídos)

import socket

# Constantes para conexão
HOST = ""
PORT = 5000

# Abrir socket pela internet, usando TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Utilizar host e porta definidos pelas constantes
sock.bind((HOST, PORT))

# Esperar uma conexão (estamos no lado 'passivo')
# Argumento indica quantidades de conexões pendentes possíveis
sock.listen(1)

# Aceita conexão
novo_sock, addr = sock.accept()
print("Conectado a [" + str(addr) + "]")

# Loop infinito para escutar N mensagens
while True:
  # Recebe mensagem do lado 'ativo'
  # Argumento indica tamanho máximo, em bytes, a ser lido
  msg = novo_sock.recv(1024)
  # Se o lado 'ativo' parou de enviar mensagens
  if not msg:
    # Sai do loop, para de escutar
    break

  print("Recebeu mensagem: '" + str(msg, encoding="utf-8") + "'")

  # Envia mensagem de volta para lado 'ativo'
  novo_sock.send(msg)
# Fim do loop infinito

print("Conexão encerrada pelo lado ativo")

# Fecha o socket da conexão
novo_sock.close()

# Fecha o socket principal
sock.close()
