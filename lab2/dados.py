# Camada 3 - Dados

import os

def getFile(path):
  # Cria dicionário de retorno
  contents = { "erro": False, "texto": "", "nome": path }
  try:
    # Lê tamanho do arquivo
    # [Ref] stackoverflow.com/a/2104083/4824627
    size = os.path.getsize(path)
    # Se for maior que o limite da conexão, sai com erro
    if size > 2048:
      raise Exception("File too large!")

    # Abre o arquivo em modo de leitura ('r') em utf-8
    with open(path,mode="r",encoding="utf-8") as file:
      # Adiciona conteúdo do arquivo para o dicionário
      contents["texto"] = file.read()
  except Exception:
    # Se houve erro ao abrir/ler o arquivo, retorna erro no dicionário
    contents["erro"] = True
  finally:
    # Retorna dicionário à camada 2
    return contents

if __name__ == "__main__":
  print("Camada 3 só funciona como módulo :)")