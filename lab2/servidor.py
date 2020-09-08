# Camada 2 - Processamento
# (adaptado da Aula 4 de Sistemas Distribuídos)

import socket
import re
import json
# [Ref] stackoverflow.com/a/56151144/4824627
from dados import getFile

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


def openServer():
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

  # Mantém a conexão aberta para receber múltiplos clientes
  while True:
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

    # Fecha o socket da conexão
    novo_sock.close()

  # Fecha o socket principal
  sock.close()

# Função a ser chamada quando o arquivo é executado
if __name__ == "__main__":
  openServer()