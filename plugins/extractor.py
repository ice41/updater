# extractor.py

import os
import zipfile

class Extractor:
    @staticmethod
    def extrair_arquivos():
        caminho_jogos = "jogos"

        # Procurar todos os arquivos .zip e arquivos fragmentados (.zip.001, etc.) em todas as subpastas
        for root, dirs, files in os.walk(caminho_jogos):
            zip_files = [f for f in files if f.endswith('.zip') or any(f.startswith('.zip.') for f in files)]
            
            if not zip_files:
                continue

            for zip_file in zip_files:
                caminho_zip = os.path.join(root, zip_file)

                try:
                    if zip_file.endswith('.zip'):
                        # Para arquivos simples .zip
                        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                            zip_ref.extractall(root)
                            print(f"{zip_file} extraído em {root}")

                    else:
                        # Para arquivos fragmentados (.zip.001, .zip.002)
                        Extractor._extrair_arquivos_fragmentados(root, zip_file)

                except zipfile.BadZipFile:
                    print(f"{zip_file} está corrompido e não pôde ser extraído.")

        print("Extração concluída. Todos os arquivos foram extraídos.")

    @staticmethod
    def _extrair_arquivos_fragmentados(folder, zip_file):
        """
        Método privado para extrair arquivos fragmentados.
        """
        zip_path = os.path.join(folder, zip_file)

        print(f"Procurando fragmentos para {zip_path}")

        # Coletar todos os arquivos fragmentados .zip.*
        arquivos_fragmentados = [f for f in os.listdir(folder) if f.startswith(zip_file.replace('.zip', '')) and f.endswith('.zip')]
        
        if arquivos_fragmentados:
            print(f"Fragmentos encontrados: {arquivos_fragmentados}")

        for fragmento in arquivos_fragmentados:
            caminho_completo = os.path.join(folder, fragmento)

            try:
                with zipfile.ZipFile(caminho_completo) as zip_parts:
                    zip_parts.extractall(folder)
            except zipfile.BadZipFile:
                print(f"{fragmento} está corrompido!")

if __name__ == "__main__":
    Extractor.extrair_arquivos()
