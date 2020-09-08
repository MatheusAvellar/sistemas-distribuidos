# Documentação

## Executando

Para executar o sistema, é necessário rodar os arquivos `cliente.py` e
`servidor.py`, ao mesmo tempo.

```
python cliente.py
```

```
python servidor.py
```

## Interação entre camadas
As camadas comunicam-se retornando objetos no seguinte formato:

```python
{
  erro: False,      # Booleana indicando o status da resposta
  texto: "(...)",   # String com mensagem de erro ou resposta
  nome: "(...).txt" # String com o nome do arquivo
}
```

No caso da interação da **camada 1** com a **camada 2**, é passado um JSON em
forma de string no campo `texto` da resposta. Exemplo:

```python
{
  "erro": False,
  "texto": "{\"uau\": 1, \"tuts\": 2, \"quero\": 1, \"ve\": 1}",
  "nome": "banana.txt"
}
```

## Lado cliente

### Camada 1 (interface)

**Input**: Nome de um ou mais arquivos para buscar.

**Output**: Lista organizada das palavras, ou mensagem de erro.

**Processamento**: Organizar lista recebida pela camada inferior, e
disponibiliza para o usuário.

## Lado servidor

### Camada 2 (processamento)

**Input**: Nome do arquivo para buscar.

**Output**: Lista (não organizada) das palavras, ou mensagem de erro.

**Processamento**: Realiza a contagem das palavras e retorna a lista das 10
palavras mais encontradas no arquivo, e a quantidade de suas ocorrências.

A lista será um dicionário/objeto com propriedades correspondentes às palavras,
e valores correspondentes às suas ocorrências.

### Camada 3 (dados)

**Input**: Nome do arquivo.

**Output**: Conteúdo do arquivo, ou mensagem de erro.

**Processamento**: Tenta ler o arquivo. Envia uma mensagem de erro se o arquivo
não existir.