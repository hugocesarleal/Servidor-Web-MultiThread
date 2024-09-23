# Servidor-Web-MultiThread
Trabalho Final da disciplina de Redes de Computadores com o objetivo de implementar um servidor web multithreaded, capaz de responder solicitações de arquivos para navegador web. O projeto foi implementado em Python, utilizando POO.

## Requisitos

- Python 3.x

## Instruções de Uso

### 1. Executar o Servidor

1. No terminal, navegue até o diretório onde o arquivo `servidor_web_multithread.py` está localizado.
2. Execute o arquivo `servidor_web_multithread.py`, informando qual será o diretório raiz. Já existe uma pasta chamada `content` junto com o arquivo `servidor_web_multithread.py`, que contém alguns arquivos para teste.

    ```bash
    python servidor_web_multithread.py C:\Users\Hugo\Desktop\Trabalho_de_Redes\content
    ```

### 2. Acessar o Servidor

- Com o servidor em funcionamento, abra um navegador de sua preferência.
- Acesse o endereço:

    ```
    http://localhost:10000
    ```

    Você será direcionado para a página HTML principal, que contém links para os outros arquivos de teste disponíveis na pasta `content`.

### 3. Acessar Arquivos Específicos

- Para acessar um arquivo específico dentro do diretório raiz, adicione o nome do arquivo e sua extensão ao final do endereço. Por exemplo, para acessar um arquivo chamado `icon.ico`, utilize:

    ```
    http://localhost:10000/icon.ico
    ```

## Encerramento do Servidor

- Para encerrar o servidor, pressione `CTRL + C` no terminal onde o servidor está em execução. Isso encerrará o socket e fechará todas as conexões ativas.

## Notas

- O servidor suporta arquivos com as seguintes extensões: `.html`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.ico`, `.mp4`, `.wav`.
- O servidor foi projetado para manter conexões persistentes para clientes que utilizam HTTP 1.1.
