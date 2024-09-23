"""
  _____________________________________________________
        Trabalho Final - Redes de Computadores

    Servidor Web Multithread - Feito por:

    Bruno Augusto de Oliveira - RA:0073211
    Hugo César Leal - RA:0072753
    Sadi Martins de Castro Garcia Mendes - RA:0073489
  _____________________________________________________

"""

import os          
import sys         
import time        
import signal      
import socket      
import threading   
import argparse 

class ServidorHTTP:
    def __init__(self, porta=10000, tamanho_pacote=1024, espera=0.00001): # Definição da porta, o tamanho dos pacotes e o tempo de espera
        self.porta = porta                      
        self.tamanho_pacote = tamanho_pacote    
        self.espera = espera                    
        self.socket_servidor = None             

    def encerrar_servidor(self, signal, frame):
        print("Encerrando servidor...")
        if self.socket_servidor:
            self.socket_servidor.close()  # Fecha o socket do servidor se estiver aberto
        sys.exit(1)                             

    def gerar_cabecalho(self, codigo_resposta, versao_http, tipo_arquivo):
        tempo_atual = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        
        # Códigos de resposta HTTP para suas descrições
        status = {
            200: "200 OK",
            404: "404 Not Found"
        }
        
        # Define o tipo de conexão com base na versão HTTP
        if versao_http == '1.1':
            tipo_conexao = 'keep-alive'
        else: tipo_conexao = 'close'
        
        # Tipos de arquivos suportados
        tipo_arquivo_mapeado = {
            'html': 'text/html; charset=utf-8',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'ico': 'image/ico',
            'mp4': 'video/mp4',
            'wav': 'audio/wav'
        }

        tipo_arquivo_mapeado.setdefault(tipo_arquivo, tipo_arquivo)

        # Cabeçalho HTTP com as informações necessárias
        cabecalho = (
            f"HTTP/{versao_http} {status.get(codigo_resposta, '500 Internal Server Error')}\n"
            f"Date: {tempo_atual}\n"
            f"Server: Servidor HTTP\n"
            f"Connection: {tipo_conexao}\n"
            f"Content-Type: {tipo_arquivo_mapeado[tipo_arquivo]}\n\n"
        )
        return cabecalho  


    def lidar_com_cliente(self, cliente_socket, endereco, diretorio_raiz):
        conexao_persistente = False  # Conexão persistente padrão desativa
        while True:
            try:
                mensagem = cliente_socket.recv(self.tamanho_pacote).decode()
                
                if not mensagem:
                    print("Nenhuma mensagem recebida, fechando conexão com o cliente...")
                    cliente_socket.close()  # Fecha o socket do cliente
                    break

                # Divide a mensagem em linhas e extrai a primeira linha
                linhas = mensagem.split('\n')
                primeira_linha = linhas[0]
                metodo_requisicao, arquivo_solicitado, versao_http = primeira_linha.split(' ')
                versao_http = versao_http[5:8]  # Extrai a versão HTTP

                print(f"Método: {metodo_requisicao}\n")
                print(f"Versão HTTP: {versao_http}")

                # Verifica se a versão HTTP suporta conexão persistente
                if versao_http == '1.1':
                    conexao_persistente = True
                    cliente_socket.settimeout(self.espera)  # Define o timeout para conexões persistentes

                if metodo_requisicao in ["GET", "HEAD"]:

                    if arquivo_solicitado == "/": # se não colocar o diretório do arquivo, direciona para a página principal
                        arquivo_solicitado = "/index.html"

                    # Separa a extensão do arquivo
                    tipo_arquivo = arquivo_solicitado.split('.')[-1]
                    # Caminho do arquivo no sistema de arquivos
                    caminho_arquivo = os.path.join(diretorio_raiz, arquivo_solicitado.lstrip('/'))
                    print(f"Arquivo solicitado: {arquivo_solicitado}\nCaminho: {caminho_arquivo}")

                    if os.path.isfile(caminho_arquivo):
                        try:
                            # Define o modo de abertura do arquivo
                            if tipo_arquivo == 'html':
                                modo = 'r' 
                            else: modo = 'rb'
                            # Abre o arquivo no modo apropriado
                            with open(caminho_arquivo, modo, encoding='utf-8') if tipo_arquivo == 'html' else open(caminho_arquivo, modo) as arquivo:
                                dados_resposta = arquivo.read()  
                            codigo_resposta = 200  # código de resposta como 200 OK
                        except Exception:
                            dados_resposta = "Erro ao ler o arquivo"  
                            codigo_resposta = 404  # código de resposta como 404 Not Found
                    else:
                        dados_resposta = "Arquivo não encontrado"  
                        codigo_resposta = 404  # código de resposta como 404 Not Found

                    # Cabeçalho da resposta HTTP
                    cabecalho_resposta = self.gerar_cabecalho(codigo_resposta, versao_http, tipo_arquivo)

                    if metodo_requisicao == "GET":
                        if tipo_arquivo == 'html':
                            corpo = dados_resposta.encode()  # Codifica o conteúdo HTML
                        else:
                            corpo = dados_resposta  # Para outros tipos de arquivos
                    else:
                        corpo = b''  # Se o método não for GET, o corpo é vazio

                    # Envia o cabeçalho e o corpo da resposta ao cliente
                    cliente_socket.send(cabecalho_resposta.encode() + corpo)

                    # Se a conexão não for persistente, fecha o socket do cliente
                    if versao_http == '1.0' or not conexao_persistente:
                        cliente_socket.close()
                        break  # Sai do loop
                else:
                    print(f"O método de requisição {metodo_requisicao} não é suportado!")
                    cliente_socket.close() 
                    break  
            except socket.timeout:
                print(f"Tempo de conexão de {self.espera} segundos excedido, fechando socket...")
                cliente_socket.close()  
                break  
            except Exception as e:
                print(f"Ocorreu um erro: {e}")
                cliente_socket.close()  
                break 

    # Inicia o servidor
    def iniciar_servidor(self, diretorio_raiz):
        # interrupção (Ctrl+C)
        signal.signal(signal.SIGINT, self.encerrar_servidor)
        
        if not os.path.isdir(diretorio_raiz): # Verifica se o diretório raiz existe
            print(f"O diretório '{diretorio_raiz}' não existe.")
            sys.exit(1)  
   
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket do servidor usando TCP
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket_servidor.bind(('localhost', self.porta))

            self.socket_servidor.listen(5)
            print(f"Servidor ouvindo na porta {self.porta}...\n")
        except Exception as e:

            print(f"Erro ao iniciar o servidor: {e}")
            self.socket_servidor.close()  
            sys.exit(1)  

        while True:
            cliente_socket, endereco = self.socket_servidor.accept()  # Aceita uma nova conexão
            print(f"Conexão recebida de {endereco}")

            threading.Thread(target=self.lidar_com_cliente, args=(cliente_socket, endereco, diretorio_raiz), daemon=True).start() #Multithread para aceitar diversas conexões

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Servidor Web Multithread') # Utilizado para informar o diretório raiz direto na linha de comando
    parser.add_argument('diretorio_raiz', type=str, help='Diretório raiz dos arquivos disponibilizados')
    args = parser.parse_args()  

    servidor = ServidorHTTP()
    
    servidor.iniciar_servidor(args.diretorio_raiz) # Inicia o servidor com o diretório raiz fornecido
