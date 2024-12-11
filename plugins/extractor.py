import os
from threading import Thread

class Extractor:
    def __init__(self, path):
        self.path = path

    def executar_tarefas_backend(self):
        def background_task():
            print(f"Iniciando tarefas no backend para o caminho: {self.path}")

            try:
                arquivos = os.listdir(self.path)
                for arquivo in arquivos:
                    print(f"Processando o arquivo {arquivo}")
                    # Coloque aqui a lógica das tarefas que deseja executar
                    # Exemplo: compactação, verificação, limpeza de arquivos, etc.

                print(f"Tarefas em segundo plano concluídas em {self.path}")

            except FileNotFoundError:
                print("Erro: caminho não encontrado.")

        Thread(target=background_task).start()
