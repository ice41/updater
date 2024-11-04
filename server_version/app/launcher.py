# launcher.py 

import os
import requests
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from utils import (get_current_version, get_server_version, download_update,
                   extract_update, move_files, remove_updater_folder, update_current_version)
from news import NewsWidget
from plugins import carregar_plugins

# URL para o app.py no GitHub
APP_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/app.py"

# URLs para verificação de estrutura
ESTRUTURA_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/estrutura_launcher.json"
BASE_DOWNLOAD_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/"  # Root directory URL

def carregar_estrutura_remota():
    """Carrega a estrutura de arquivos e versões mais recentes do launcher do GitHub."""
    try:
        response = requests.get(ESTRUTURA_URL)
        response.raise_for_status()
        return response.json()  # Retorna a estrutura como um dicionário
    except requests.RequestException as e:
        print(f"Erro ao carregar estrutura remota: {e}")
        return {}

def verificar_arquivos_locais(estrutura_remota):
    """Verifica e atualiza a estrutura do launcher com base na estrutura remota."""
    faltando = []
    desatualizados = []

    for pasta, arquivos in estrutura_remota.items():
        caminho_pasta = os.path.join(".", pasta)
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta, exist_ok=True)
            print(f"Criada pasta: {caminho_pasta}")

        for arquivo_info in arquivos:
            nome_arquivo = arquivo_info["nome"]
            versao_arquivo = arquivo_info["versao"]
            caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)

            if not os.path.exists(caminho_arquivo):
                faltando.append((caminho_arquivo, versao_arquivo))
            else:
                # Verificar a versão do arquivo se for indicado no JSON
                with open(caminho_arquivo, "r") as f:
                    conteudo = f.read()
                if f"versao: {versao_arquivo}" not in conteudo:
                    desatualizados.append((caminho_arquivo, versao_arquivo))
    
    return faltando, desatualizados

def atualizar_arquivos(faltando, desatualizados):
    """Baixa e atualiza os arquivos faltando ou desatualizados."""
    for caminho_arquivo, versao in faltando + desatualizados:
        # Cria a URL completa para cada arquivo baseado no caminho
        nome_relativo = os.path.relpath(caminho_arquivo, ".")  # Caminho relativo a partir da raiz
        url_arquivo = f"{BASE_DOWNLOAD_URL}{nome_relativo.replace(os.sep, '/')}"
        
        # Garante que o diretório para o arquivo exista
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

        try:
            response = requests.get(url_arquivo)
            response.raise_for_status()

            # Salva o conteúdo do arquivo no local desejado
            with open(caminho_arquivo, "wb") as f:
                f.write(response.content)

            print(f"Arquivo atualizado: {caminho_arquivo} para a versão {versao}")
        except requests.RequestException as e:
            print(f"Erro ao baixar {url_arquivo}: {e}")

def executar_verificacao_estrutura():
    """Função principal para verificar e atualizar a estrutura do launcher automaticamente."""
    estrutura_remota = carregar_estrutura_remota()
    if not estrutura_remota:
        print("Erro: Não foi possível carregar a estrutura remota.")
        return

    faltando, desatualizados = verificar_arquivos_locais(estrutura_remota)

    if faltando or desatualizados:
        print("Atualizando arquivos do launcher...")
        atualizar_arquivos(faltando, desatualizados)
        print("Atualização concluída!")
    else:
        print("Estrutura do launcher já está atualizada.")

def load_and_run_app():
    """Lê e executa o app.py diretamente do GitHub."""
    try:
        response = requests.get(APP_URL)
        response.raise_for_status()  # Garante que o download foi bem-sucedido
        exec(response.text, globals())  # Executa o código de app.py diretamente na memória
    except requests.RequestException as e:
        print(f"Erro ao carregar o app.py: {e}")

if __name__ == "__main__":
    executar_verificacao_estrutura()  # Executa a verificação de estrutura antes de carregar o app principal
    load_and_run_app()
