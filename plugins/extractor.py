# extractor.py

import os
import zipfile

class Extractor:
    @staticmethod
    def extrair_arquivos():
        caminho_jogos = "jogos"
        zip_files = [f for f in os.listdir(caminho_jogos) if f.endswith('.zip')]

        if not zip_files:
            print("Nenhum arquivo .zip encontrado para extrair.")
            return

        for zip_file in zip_files:
            caminho_zip = os.path.join(caminho_jogos, zip_file)
            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    zip_ref.extractall(caminho_jogos)
                    print(f"{zip_file} extraído com sucesso.")
            except zipfile.BadZipFile:
                print(f"{zip_file} está corrompido e não pôde ser extraído.")

        print("Extração concluída. Todos os arquivos .zip foram extraídos.")
