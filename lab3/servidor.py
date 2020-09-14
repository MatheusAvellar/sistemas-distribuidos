# Camada 2 - Processamento
# (adaptado dos módulos 2 e 3 de Sistemas Distribuídos)

import socket
import re
import json
import select
import sys
import threading
# [Ref] stackoverflow.com/a/56151144/4824627
from dados import getFile

#######################################

def processFilenames(msg):
  # Separa nomes de arquivos em lista (quebrando onde há vírgulas)
  sp = msg.split(",")
  # Remove espaço em branco extra ('    b.txt ')
  # [Ref] stackoverflow.com/a/761825/4824627
  for k,v in enumerate(sp):
    sp[k] = v.strip()

  print(sp)
  # Retorna nomes de arquivos tratados
  return sp

def processText(content):
  # Transforma todas as letras em minúsculas e, em seguida, separa palavras
  # (separando-as em caracteres que não são letras)
  sp = re.split(r"[^a-záàãéèíìóòõúùç\-]+", content.lower())
  dic = {}
  # Itera sobre todas as palavras no texto
  for k,v in enumerate(sp):
    if len(v) > 0 and v != '-':
      # [Ref] stackoverflow.com/a/1602964/4824627
      dic[v] = dic.get(v,0) + 1
  return dic

#######################################

# Constantes para conexão
HOST = ""
PORT = 5000

# Lista de I/O a serem escutados (com select)
entradas = [sys.stdin]
# Conexões ativas no momento
conexoes = {}
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

def acceptConnection(sock):
  # Aceita conexão nova
  clisock, endr = sock.accept()

  # Adiciona ao dicionário de conexões (com lock para prevenir race-condition)
  lock.acquire()
  conexoes[clisock] = endr 
  lock.release()

  # Retorna socket e endereço do novo cliente
  return clisock, endr

def handleClient(novo_sock, addr):
  # Loop infinito para escutar N mensagens
  while True:
    # Recebe mensagem do lado 'ativo'
    # Argumento indica tamanho máximo, em bytes, a ser lido
    msg = novo_sock.recv(1024)

    # Se o lado 'ativo' parou de enviar mensagens
    if not msg:
      # Retira o cliente da lista de conexões ativas
      lock.acquire()
      del conexoes[novo_sock]
      lock.release()
      # Encerra a conexão com o cliente
      novo_sock.close()
      print(str(addr) + " -> encerrou conexão")
      return

    msg = str(msg, encoding="utf-8")

    print("Recebeu mensagem: '" + msg + "'")

    # Trata nomes de arquivo recebidos
    arquivos = processFilenames(msg)

    # Para cada arquivo passado, tenta pegar o conteúdo
    for k,v in enumerate(arquivos):
      retorno = getFile(v)
      resp = { "erro": False, "texto": "", "nome": v }
      # Se camada 3 retornou erro, envia erro para camada 1
      if retorno["erro"] == True:
        resp["erro"] = True
        resp["texto"] = "[!] Erro lendo arquivo " + v
      else:
        # Processa o texto, e transforma em string
        strng = json.dumps(processText(retorno["texto"]))
        resp["texto"] = strng
      print(resp)
      # Envia mensagem de volta para lado 'ativo'
      novo_sock.send(json.dumps(resp).encode())

  # Fim do loop infinito
  print("Conexão encerrada pelo lado ativo")

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
      print("Conexões: " + str(conexoes.values()))
  elif cmd == "hist":
    print(str(conexoes.values()))
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
        print("Conectado a [" + str(addr) + "]")
        # Cria thread para atender o novo cliente
        cliente = threading.Thread(target=handleClient, args=(novo_sock,addr))
        cliente.start()
      elif io_recebido == sys.stdin: # Acesso direto pelo terminal
        cmd = input()
        processCommand(cmd,sock)

# Função a ser chamada quando o arquivo é executado
if __name__ == "__main__":
  openServer()