import socket
import select
import sys
import threading
from color import colors

# [Ref] stackoverflow.com/a/11532079/4824627
class CustomDict(dict):
  pass

config = CustomDict()
# Constantes gerais
config.DEFAULT_PORT = 42000
config.NODE_COUNT = 4
config.exit = False
config.requested_hat = False
# Variável importante a ser replicada
config.X = 0
config.received_X = 0
# Array de requisições locais para modificar o valor de X
config.X_request = []

def tryOpenSocket():
  global config

  try:
    # Abre um socket para esse nó receber conexões
    config.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    config.sock.bind(("",config.port))
    config.sock.listen(5)
    config.sock.setblocking(False)
    config.inputs.append(config.sock)
    return True
  except OSError:
    print(f"Porta inacessível! Talvez tente escolher outro ID?")
    return False

def main():
  global config

  # Inputs que o nó deverá observar
  config.inputs = [ sys.stdin ]
  # Variável de controle se o nó atual é o primário
  config.am_i_primary = False

  # Recebe ID da réplica do usuário
  while True:
    try:
      print("ID da réplica: ", end="", flush=True)
      config.node_id = int(input())
      if config.node_id < 1 or config.node_id > config.NODE_COUNT:
        print(f"Insira um número entre 1 e {config.NODE_COUNT}!")
        continue
      config.port = config.DEFAULT_PORT + config.node_id
      if not tryOpenSocket():
        continue
      break
    except ValueError:
      print(f"Insira um número entre 1 e {config.NODE_COUNT}!")

  # Atualiza status de "cópia primário"
  config.am_i_primary = True if config.node_id == 1 else False

  # Cria cópia local do endereço de todos os nós
  config.nodes = {}
  for i in range(config.NODE_COUNT):
    config.nodes[i+1] = ("",config.DEFAULT_PORT+i+1)

  # Histórico de modificações de X
  config.X_modif_hist = []

  _str_is_primary = " (cópia primária)" if config.am_i_primary else ""
  print(f"Criado nó ID={config.node_id}, porta={config.port}, X={config.X}{_str_is_primary}")

  printHelp()

  try:
    while True:
      # Espera por qualquer entrada de interesse
      r,w,e = select.select(config.inputs, [], [])
      # Trata todas as entradas prontas
      for ready in r:
        if ready == config.sock:
          new_sock,addr = config.sock.accept()
          cliente = threading.Thread(target=acceptConn, args=(new_sock,addr))
          cliente.start()
        elif ready == sys.stdin:
          processCommand(input())
          if config.exit:
            raise KeyboardInterrupt("Saída requisitada")
  except KeyboardInterrupt:
    print(f"Nó {config.node_id} encerrado!")
    return

def printHelp():
  systemPrint("Comandos disponíveis:")
  print(f"\t{colors.fg.lightgreen}help\n{colors.reset}\t\tImprime essa lista")
  print(f"\t{colors.fg.lightgreen}x\n{colors.reset}\t\tImprime o valor atual de X nessa réplica")
  print(f"\t{colors.fg.lightgreen}history\n{colors.reset}\t\tImprime o histórico de valores de X")
  print(f"\t{colors.fg.lightgreen}set [n]\n{colors.reset}\t\tAltera o valor de X")
  print(f"\t\tEx.: '{colors.fg.lightgreen}set 10{colors.reset}' altera o valor para 10")
  print(f"\t{colors.fg.lightgreen}ping\n{colors.reset}\t\tRequisita uma resposta de todas as réplicas ativas")
  print(f"\t{colors.fg.lightgreen}exit\n{colors.reset}\t\tFinaliza o programa")
  print(colors.reset)

def systemPrint(msg):
  print(f"{colors.fg.lightblue}>> {msg}{colors.reset}")

def processCommand(cmd):
  global config

  cmd = f"{cmd}".lower()
  if cmd == "help":
    printHelp()
  elif cmd == "x":
    systemPrint(f"X = {config.X}")
  elif cmd == "history":
    systemPrint(config.X_modif_hist)
  elif cmd == "ping":
    sendAll("ping")
  elif cmd == "exit":
    if not config.am_i_primary:
      systemPrint("Até a próxima!")
      config.exit = True
    else:
      systemPrint(f"É cópia primária - não pode sair (Ctrl-C caso seja a última instância)")
  elif cmd.startswith("set"):
    str_val = cmd.split(" ")[1]
    # Tenta converter valor recebido para int
    try:
      val = int(str_val)
    except ValueError:
      systemPrint(f"Valor '{str_val}' inválido! Não é um número inteiro!")
      return
    # Escreve valor novo de X
    writeX(val)

def writeX(val):
  global config

  if config.am_i_primary:
    config.X = val
    config.X_modif_hist.append([config.node_id, val])
    systemPrint("X atualizado!")
  else:
    if config.requested_hat:
      # Já requisitou chapéu
      systemPrint("Não é cópia primária ainda, esperando 'chapéu'...")
    else:
      systemPrint("Não é cópia primária, requisitando 'chapéu'...")
    # Adiciona valor à lista de requisições de modificação de X
    config.X_request.append(val)
    # Requisita chapéu para todos os nós
    sendAll("want-hat")
    # Já requisitou chapéu
    config.requested_hat = True

def acceptConn(new_sock,addr):
  global config

  while True:
    data = new_sock.recv(1024)
    if not data:
      new_sock.close()
      break
    req = str(data, encoding="utf-8").split(",")
    from_id = int(req[0])
    req = req[1]
    print(f"  {config.node_id}🖥️ <-  🌎{from_id} {colors.fg.lightgreen}{req}{colors.reset}")
    processRequest(from_id, req)

def processRequest(from_id, req):
  global config

  # Atualização do valor de X
  if req.startswith("update-x") and not config.am_i_primary:
    try:
      val = int(req.split(" ")[1])
    except ValueError:
      return
    # Atualiza o valor local de X
    config.X = val
    config.received_X = val
    # Atualiza a lista de modificações de X
    config.X_modif_hist.append([from_id, val])
  elif req == "ping":
    # Responde requisição de ping
    sendToID(from_id,f"pong!")
  elif config.am_i_primary and req.startswith("want-hat"):
    # Se o valor foi modificado desde que o nó recebeu o chapéu
    if config.X != config.received_X:
      # Atualiza todos os nós sobre o valor atual de X
      sendAll(f"update-x {config.X}")
    # Não é mais o primário
    config.am_i_primary = False
    # Manda o chapéu para o nó que requisitou
    sendToID(from_id,f"give-hat {config.X}")
    systemPrint(f"Chapéu enviado para {from_id}")
  elif req.startswith("give-hat") and not config.am_i_primary:
    # Último valor de X do nó anterior
    val = int(req.split(" ")[1])
    # Se for diferente do último valor no histórico
    if config.X_modif_hist[-1][1] != val:
      # Adiciona ao histórico
      config.X_modif_hist.append([from_id, val])

    # Recebeu chapéu!
    config.am_i_primary = True
    # Atualiza requisições que o cliente fez enquanto não tinha chapéu
    for i in range(len(config.X_request)):
      val = config.X_request[i]
      config.X = val
      config.X_modif_hist.append([config.node_id, val])
    config.X_request = []
    systemPrint("Chapéu recebido! Valor de X foi atualizado conforme requisitado")

def sendAll(msg):
  global config

  for i in range(len(config.nodes)):
    if i+1 == config.node_id:
      continue
    sendToID(i+1,msg)

def sendToID(nid,msg):
  global config

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect(config.nodes[nid])
  except Exception:
    return
  print(f"  {config.node_id}🖥️  -> 🌎{nid} {colors.fg.lightgreen}{msg}{colors.reset}")
  msg = f"{config.node_id},{msg}"
  sock.send(msg.encode())
  sock.close()

if __name__ == "__main__":
  main()