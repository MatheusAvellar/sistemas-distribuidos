# Camada 2 - Processamento
# (adaptado dos módulos 2 e 3 de Sistemas Distribuídos)

import socket
import re
import json
import select
import sys
import threading

# Constantes para conexão
HOST = ""
PORT = 5001

# Lista de I/O a serem escutados (com select)
entradas = [sys.stdin]
# Conexões ativas no momento
conexoes = {}
clisocks = {}
# Lock para acesso a 'conexoes'
lock = threading.Lock()
# Flag indicando se o servidor está em processo de encerrar
finalizando = False

def createServer():
  # Abrir socket pela internet, usando TCP
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Utilizar host e porta definidos pelas constantes
  sock.bind((HOST, PORT))

  # Esperar uma conexão (estamos no lado 'passivo')
  # Argumento indica quantidades de conexões pendentes possíveis
  sock.listen(5)

  # Socket em modo não-bloqueante
  sock.setblocking(False)

  # inclui o socket principal na lista de entradas de interesse
  entradas.append(sock)

  return sock

# Cria lista de IDs (incrementais) para clientes
available_ids = list(range(1, 51))

# Pega o primeiro item e o remove da lista
def getNewId():
  return available_ids.pop(0)

# Retorna o ID para a lista de disponíveis
def releaseId(id):
  available_ids.append(id)

def acceptConnection(sock):
  # Aceita conexão nova
  clisock, addr = sock.accept()

  lock.acquire()
  # Gera ID para o cliente
  new_id = getNewId()
  # Adiciona ao dicionário de conexões
  conexoes[clisock] = {
    "addr": addr,
    "id": new_id
  }
  clisocks[new_id] = clisock
  lock.release()

  # Envia seu ID e lista de usuários ativos para o cliente
  users = [u["id"] for u in list(conexoes.values())]
  clisock.send(str.encode(f"{new_id},{users}"))

  print(f"{new_id} entrou - {str(addr)}")
  tellEveryoneText("new", new_id)

  # Retorna socket e endereço do novo cliente
  return clisock, addr

def getUserList():
  return [u["id"] for u in list(conexoes.values())]

def handleClient(novo_sock, addr):
  client_id = conexoes[novo_sock]["id"]
  # Loop infinito para escutar N mensagens
  while True:
    # Recebe mensagem do lado 'ativo'
    # Argumento indica tamanho máximo, em bytes, a ser lido
    msg = novo_sock.recv(1024)
    # Se o lado 'ativo' parou de enviar mensagens
    if not msg:
      lock.acquire()
      # Retorna o ID do cliente à lista de IDs disponíveis
      releaseId(client_id)
      # Retira o cliente da lista de conexões ativas
      del conexoes[novo_sock]
      del clisocks[client_id]
      lock.release()
      # Encerra a conexão com o cliente
      novo_sock.close()
      print(f"{client_id} saiu")
      tellEveryoneText("out", client_id)
      return

    msg = str(msg, encoding="utf-8")
    print(msg)
    spl = msg.split(",{")
    indicated_length = int(spl[0])
    str_json = "{" + spl[1]
    # Caso o JSON a ser recebido tenha tamanho maior que 1024, precisamos de
    # várias chamadas a recv() para lê-lo por completo
    while indicated_length - len(str_json) > 0:
      str_json = str_json + str(novo_sock.recv(1024), encoding="utf-8")

    parsed = json.loads(str_json)
    text = parsed["text"]
    to = int(parsed["to"])
    fro = int(parsed["id"])

    # Se o destinatário não é o servidor
    if to != 0:
      # Se o destinatário está na lista de conexões
      if to in clisocks:
        print(f"{client_id} -> {to}: {text}")
        clisocks[to].send(str.encode(f"{indicated_length},{str_json}"))
      else:
        print(f"Usuário {to} não existe!")
    # Senão, é para o servidor inteiro
    else:
      if parsed["type"] == "cmd":
        if text == "/hist":
          users = getUserList()
          ret_json = json.dumps({
            "id": 0,
            "to": fro,
            "type": "cmd",
            "cmd": text,
            "text": f"Conexões ativas ({len(users)}):\n\t{str(users)}"
          })
          clisocks[fro].send(str.encode(f"{len(ret_json)},{ret_json}"))
      else:
        print(f"{client_id} -> Server: {text}")
        tellEveryoneJSON(str_json)

  # Fim do loop infinito
  print("Conexão encerrada pelo lado ativo")

def tellEveryoneText(type,text):
  for i,id in enumerate(clisocks):
    envelope = json.dumps({
      "id": 0,
      "to": id,
      "type": type,
      "text": text
    })
    clisocks[id].send(str.encode(f"{len(envelope)},{envelope}"))

def tellEveryoneJSON(str_json):
  for i,id in enumerate(clisocks):
    clisocks[id].send(str.encode(f"{len(str_json)},{str_json}"))

def printActiveConnections():
  print(f"Conexões ativas ({len(conexoes.values())}):\n\t{str(list(conexoes.values()))}")

def processCommand(cmd,sock):
  # Comando para terminar o servidor
  if cmd == "exit":
    # Se nenhum cliente estiver conectado mais
    if not conexoes:
      # Fecha o socket principal
      sock.close()
      # Sai do programa
      sys.exit()
    else:
      # Avisa que ainda há conexões ativas
      print("Ainda existem conexões ativas!")
      printActiveConnections()
  elif cmd == "hist":
    printActiveConnections()
  elif cmd == "wids":
    print(f"IDs ainda disponíveis ({len(available_ids)}):\n\t",end="")
    print(available_ids)
  elif cmd == "help":
    printHelp()
  elif cmd == "vaca":
    print("")
    print(" _________________________")
    print("| Oi tia tudo bom contigo |")
    print(" -------------------------")
    print("        \\   ^__^")
    print("         \\  (oo)\\_______")
    print("            (__)\\       )\\/\\")
    print("                ||----w |")
    print("                ||     ||")
    print("")

def printHelp():
  print("Comandos:")
  print("\texit\n\t\tFecha o servidor se não houverem conexões ativas")
  print("\thist\n\t\tLista conexões ativas")
  print("\twids\n\t\tLista IDs ainda disponívei para clientes")
  print("\thelp\n\t\tImprime esta lista")
  print("\tvaca\n\t\tUma vaquinha")

def openServer():
  print("Iniciando servidor")
  printHelp()
  print("-"*8)
  sock = createServer()
  # Mantém a conexão aberta para receber múltiplos clientes
  while True:
    # Escuta todos os I/Os da lista
    leitura, _, _ = select.select(entradas, [], [])

    # Itera sobre as entradas prontas
    for io_recebido in leitura:
      # Novo pedido de conexão (novo cliente)
      if io_recebido == sock:
        # Aceita conexão e pega socket e endereço do novo cliente
        novo_sock, addr = acceptConnection(sock)
        # Cria thread para atender o novo cliente
        cliente = threading.Thread(target=handleClient, args=(novo_sock,addr))
        cliente.start()
      # Acesso direto pelo terminal
      elif io_recebido == sys.stdin:
        cmd = input()
        processCommand(cmd,sock)

# Função a ser chamada quando o arquivo é executado
if __name__ == "__main__":
  openServer()