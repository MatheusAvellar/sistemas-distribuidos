# Camada 1 - Interface
# (adaptado do módulo 2 de Sistemas Distribuídos)

import socket
import json
import select
import sys
from color import colors

HOST = "localhost"
PORT = 5001
config = {
  "dest_id": 0,
  "client_id": 0
}

# Lista de I/O a serem escutados (com select)
entradas = [sys.stdin]


def printHelp():
  print(colors.fg.lightblue,"-"*10,colors.reset)
  print("Comandos:")
  print("\t/chat <id>\n\t\tPassa a se comunicar com o usuário de id especificado")
  print(              "\t\tID = 0 se refere ao servidor, i.e. todos os usuários")
  print(              "\t\tO canal padrão é o servidor")
  print(              "\t\tEx.: /chat 0")
  print("\t/exit\n\t\tFecha a conexão com o servidor")
  print("\t/help\n\t\tImprime essa lista")
  print("\t/hist\n\t\tRequisita a lista de usuários para o servidor")
  print(colors.fg.lightblue,"-"*10,colors.reset)

def getServerFromId(id):
  if id == 0: return f"{colors.fg.purple}Server{colors.reset}"
  if id == config["client_id"]: return f"{colors.fg.cyan}Você{colors.reset}"
  return f"{colors.fg.lightblue}User {id}{colors.reset}"

def changeChat(id):
  try:
    config["dest_id"] = int(id)
    print(f"Canal modificado para '{getServerFromId(int(id))}'")
  except ValueError as verr:
    print(f"Valor '{id}' não é um ID válido :(")


# Recebe um JSON (já em forma de string) e envia pelo socket
def sendMessage(sock,envelope):
  sock.send(str.encode(f"{len(envelope)},{envelope}"))


def processCommand(msg,sock):
  # Se o usuário digitar '/help', imprime a ajuda
  if msg == "/help":
    printHelp()
    return
  # Se o usuário digitar '/chat', tenta trocar destinatário
  if msg[:5] == "/chat":
    changeChat(msg[5:].strip())
    return

  if msg == "/hist":
    sendMessage(sock,json.dumps({
      "id": config["client_id"],
      "to": 0,
      "type": "cmd",
      "text": msg
    }))
    return

  print(f"Commando desconhecido '{msg}'")


def processText(msg,sock):
  # Se a mensagem está vazia, pula
  if len(msg) == 0:
    return

  # Se for algum outro comando, trata adequadamente
  if msg[0] == '/':
    processCommand(msg,sock)
    return

  # Senão, envia mensagem para o servidor
  sendMessage(sock,json.dumps({
    "id": config["client_id"],
    "to": config["dest_id"],
    "type": "msg",
    "text": msg
  }))

  to = getServerFromId(config["dest_id"])
  fro = getServerFromId(config["client_id"])
  # Sobrescrever a linha anterior (i.e. o texto que o cliente acabou de inserir)
  print("\033[1F",end="")
  # Imprime a mensagem com coeficiente de floricultura
  print(f"[{to}] {fro}: {msg}")


def handleReceivedMessage(text):
  if not text: return True
  spl = text.split(",{")
  indicated_length = int(spl[0])
  str_json = "{" + spl[1]
  # Caso o JSON a ser recebido tenha tamanho maior que 1024, precisamos de
  # várias chamadas a recv() para lê-lo por completo
  while indicated_length - len(str_json) > 0:
    str_json = str_json + str(novo_sock.recv(1024), encoding="utf-8")

  cjson = json.loads(str_json)
  text = cjson["text"]
  to = getServerFromId(cjson["to"])
  fro = getServerFromId(cjson["id"])

  if cjson["type"] == "msg":
    # Se a mensagem é do próprio usuário, ignora
    if int(cjson["id"]) == config["client_id"]:
      return

    print(f"[{to}] {fro}: {text}")
  else:
    # Se um usuário entrou
    if cjson["type"] == "new":
      print(f"{getServerFromId(int(text))} entrou")
    # Se um usuário saiu
    elif cjson["type"] == "out":
      print(f"{getServerFromId(int(text))} saiu")
    # Resposta para comandos enviados ao servidor
    elif cjson["type"] == "cmd":
      print(text)



def openClient():
  # Abrir socket pela internet, usando TCP
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Conecta-se ao host e porta definidos pelas constantes
  sock.connect((HOST, PORT))
  # Adiciona socket à lista de entradas a serem observadas pelo 'select'
  entradas.append(sock)

  # Imprime texto de ajuda
  printHelp()

  # Recebe ID designado pelo servidor
  greeting = str(sock.recv(1024), encoding="utf-8")
  str_id = greeting.split(",")[0]
  new_id = int(str_id)
  config["client_id"] = new_id
  print(f"\nVocê é o usuário de ID #{colors.fg.cyan}{new_id}{colors.reset}")

  # TODO: se a lista tiver mais que 1024 bytes, precisa reorganizar isso
  users = json.loads(greeting[(len(str_id)+1):])
  print(f"Conexões ativas ({len(users)}):  {users}")

  working_input = ""

  # Loop infinito para enviar N mensagens
  while True:
    current_server = getServerFromId(config["dest_id"])

    # Escuta todos os I/Os da lista
    leitura, _, _ = select.select(entradas, [], [])

    # Itera sobre as entradas prontas
    for io_recebido in leitura:
      # Mensagem recebida do servidor
      if io_recebido == sock:
        r = handleReceivedMessage(str(sock.recv(1024), encoding="utf-8"))
        if r: break
      # Acesso direto pelo terminal
      elif io_recebido == sys.stdin:
        # Se o usuário digitar '/exit', sai do loop
        msg = input().strip()
        if msg == "/exit":
          break
        # Senão, processa o texto enviado
        processText(msg,sock)
        continue
    else:
      # Se o loop interno não foi quebrado, continua o 'while'
      continue
    # O loop interno foi quebrado, termina o 'while'
    # [Ref] stackoverflow.com/a/3150107/4824627
    break

  # Fecha a conexão
  sock.close()


# Função a ser chamada quando o arquivo é executado
if __name__ == "__main__":
  openClient()