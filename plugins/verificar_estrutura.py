# verificar_estrutura.py

import os
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup


# URL do JSON que lista a estrutura e versões dos arquivos do launcher
ESTRUTURA_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/estrutura_launcher.json"
BASE_DOWNLOAD_URL = "https://raw.githubusercontent.com/ice41/updater/branch/"

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
                if "versao" in arquivo_info:
                    with open(caminho_arquivo, "r") as f:
                        conteudo = f.read()
                    if f"versao: {versao_arquivo}" not in conteudo:
                        desatualizados.append((caminho_arquivo, versao_arquivo))
    
    return faltando, desatualizados

def atualizar_arquivos(faltando, desatualizados):
    """Baixa e atualiza os arquivos faltando ou desatualizados."""
    for caminho_arquivo, versao in faltando + desatualizados:
        url_arquivo = BASE_DOWNLOAD_URL + caminho_arquivo.replace("\\", "/").lstrip("./")
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

        try:
            response = requests.get(url_arquivo)
            response.raise_for_status()

            with open(caminho_arquivo, "wb") as f:
                f.write(response.content)

            print(f"Atualizado: {caminho_arquivo} para a versão {versao}")
        except requests.RequestException as e:
            print(f"Erro ao baixar {caminho_arquivo}: {e}")

def executar():
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

class VerificarEstruturaWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10

        # Label de status
        self.status_label = Label(text="Verificando estrutura do launcher...", size_hint_y=None, height=40)
        self.add_widget(self.status_label)

        # Inicia a verificação e atualização automática ao carregar
        self.verificar_e_atualizar()

    def verificar_e_atualizar(self):
        estrutura_remota = carregar_estrutura_remota()
        if not estrutura_remota:
            self.show_popup("Erro", "Não foi possível carregar a estrutura remota.")
            return

        # Verifica arquivos faltando e desatualizados
        faltando, desatualizados = verificar_arquivos_locais(estrutura_remota)

        # Atualiza se necessário
        if faltando or desatualizados:
            self.status_label.text = "Atualizando arquivos do launcher..."
            atualizar_arquivos(faltando, desatualizados)
            self.status_label.text = "Atualização concluída!"
        else:
            self.status_label.text = "Estrutura do launcher já está atualizada."

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

# Função principal do plugin
def executar():
    """Função principal do plugin para verificar e atualizar a estrutura do launcher."""
    widget = VerificarEstruturaWidget()
    popup = Popup(title="Verificar Estrutura do Launcher", content=widget, size_hint=(0.9, 0.9))
    popup.open()

