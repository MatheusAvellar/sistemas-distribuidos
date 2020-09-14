# Camada 1 - Interface
# (adaptado do módulo 2 de Sistemas Distribuídos)

import socket
import json

HOST = "localhost"
PORT = 5000

def processList(dic):
  # Ordena a lista, e pega os 10 primeiros elementos
  # [Ref] stackoverflow.com/a/613218/4824627
  # [Ref] stackoverflow.com/a/12980510/4824627
  res = {k: v for k, v in sorted(dic.items(), key=lambda item: item[1], reverse=True)[:10]}
  # Itera sobre o dicionário para pegar os 10 itens com maior ocorrência
  for k,v in enumerate(res):
    # Imprime "[ocorrências]: [palavra]"
    print(str(res[v]) + ": " + str(v))

  # Imprime separador
  print("-"*15)


def openClient():
  # Abrir socket pela internet, usando TCP
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Conecta-se ao host e porta definidos pelas constantes
  sock.connect((HOST, PORT))

  print("Digite nomes de arquivos a serem processados")
  print("Para múltiplos arquivos, separe os nomes por vírgulas")
  print("Ex.: exemplos/banana.txt, exemplos/lei.txt")

  # Loop infinito para enviar N mensagens
  while True:
    # Recebe input do usuário
    print("\nDigite 'exit' para fechar a conexão")
    print("Arquivos: ", end="")
    msg = input()

    # Se o usuário digitar 'exit', sai do loop
    if msg == "exit":
      break

    # Senão, envia input para o lado 'passivo'
    sock.send(str.encode(msg))

    # Espera N respostas do lado 'passivo'
    # 'N' é a quantidade de palavras, separadas por vírgula, que o usuário passou
    for i in range(0, len(msg.split(","))):
      # Argumento de `recv` indica tamanho máximo, em bytes, a ser lido
      json_resp = str(sock.recv(3072), encoding="utf-8")

      # Converte string JSON em dicionário de python
      resp = json.loads(json_resp)
      if resp["erro"]:
        # Se houve erro, reporta e continua
        print("Ocorreu um erro ao ler o arquivo '" + resp["nome"] + "'")
        print("Erro: " + resp["texto"])
      else:
        # Senão, inicia resposta para o usuário
        print("As 10 palavras com mais ocorrências no arquivo '" + resp["nome"] + "' são:")
        # E chama a função que vai ordenar a lista
        processList(json.loads(resp["texto"]))

  # Fecha a conexão
  sock.close()

# Função a ser chamada quando o arquivo é executado
if __name__ == "__main__":
  openClient()