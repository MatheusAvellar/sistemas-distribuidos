# Trabalhos de Sistemas Distribuídos

## lab1

Servidor de echo simples, em python. Retorna mensagens enviadas pelo cliente.

## lab2

Servidor que conta a ocorrência de palavras em um dado arquivo, se ele existir.
Feito em 3 camadas, onde camada 1: interface com o usuário; camada 2: servidor
para processamento e camada 3: módulo que acessa os arquivos.

## lab3

O exato mesmo projeto do lab anterior, porém transformando o servidor em
concorrente, isto é, vários clientes podem se conectar ao mesmo tempo ao
servidor.

## lab4

Implementação de um programa de chat, que utiliza um servidor central para
receber e distribuir as mensagens. Vários clientes podem se conectar ao mesmo
tempo, e enviar mensagens para outros clientes especificamente.

## lab5

Implementação simplificada do protocolo Chord, que especifica uma tabela hash
distribuída entre um anel de vários nós.

## lab6

Protocolo de replicação baseado em cópia primária com escrita local – isto é,
sistema onde há cópia de dados distribuída entre vários processos separados.
Há uma cópia definida como "primária" que controla escritas ao dado; quando
outra cópia deseja modificar o dado, ela antes requisita o status de "primária".