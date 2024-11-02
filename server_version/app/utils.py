# utils.py

import os
import sys
import requests
import zipfile
import shutil
import subprocess
import time
import psutil  # Biblioteca para gerenciar processos

VERSION_FILE_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/versao.txt"
UPDATE_URL = "https://github.com/ice41/updater/archive/refs/heads/main.zip"
OLD_VERSION = "0.0.24"
VERSAO_ATUAL = "0.0.25"

def get_current_version():
    version_file_path = 'versao.txt'
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as f:
            return f.read().strip()
    else:
        with open(version_file_path, 'w') as f:
            f.write(VERSAO_ATUAL)
        return VERSAO_ATUAL

def get_server_version():
    try:
        response = requests.get(VERSION_FILE_URL)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print("Erro ao verificar a versão.")
    return None

def download_update(update_progress_callback=None):
    try:
        response = requests.get(UPDATE_URL, stream=True)
        total_length = int(response.headers.get('content-length', 0))
        if response.status_code == 200:
            with open('atualizacao.zip', 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if update_progress_callback and total_length > 0:
                            progress = int((downloaded / total_length) * 50)  # Progresso até 50%
                            update_progress_callback(progress)
            return True
        else:
            print("Erro: não foi possível baixar o arquivo.")
            return False
    except Exception as e:
        print(f"Erro ao baixar a atualização: {e}")
        return False

def extract_update():
    try:
        with zipfile.ZipFile('atualizacao.zip', 'r') as zip_ref:
            zip_ref.extractall('updater-main')
            return True
    except Exception as e:
        print("Erro ao extrair a atualização: " + str(e))
        return False

def move_files(update_progress_callback=None):
    source_dir = 'updater-main/updater-main'
    total_files = len(os.listdir(source_dir))
    moved_files = 0
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join('.', item)
        try:
            shutil.move(s, d)
            moved_files += 1
            if update_progress_callback and total_files > 0:
                progress = 50 + int((moved_files / total_files) * 50)  # Progresso de 50% a 100%
                update_progress_callback(progress)
        except Exception as e:
            print(f"Erro ao mover arquivos: {e}")

def update_current_version(new_version):
    with open('versao.txt', 'w') as f:
        f.write(new_version)

def remove_updater_folder():
    """Remove as pastas temporárias usadas durante a atualização"""
    folders_to_remove = ['updater-main', 'links', 'news', 'server_version']
    for folder in folders_to_remove:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Removido: {folder}")
            except Exception as e:
                print(f"Erro ao remover a pasta {folder}: {e}")

# Executa o processo de atualização
if __name__ == "__main__":
    if get_server_version() != get_current_version():
        if download_update():
            if extract_update():
                move_files()
                update_current_version(VERSAO_ATUAL)
                restart_launcher()
