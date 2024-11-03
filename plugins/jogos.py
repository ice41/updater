# plugins.py

import os
import importlib
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

# URL do JSON com os arquivos necessários para cada jogo
JOGOS_NECESSARIOS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/jogos_necessarios.json"

# Defina os plugins que devem aparecer no menu
PLUGINS_VISIVEIS = ["Jogos cracked"]  # Exemplo: substituir pelos nomes dos plugins desejados

# Nome do plugin que deve executar automaticamente sem aparecer no menu
PLUGIN_VERIFICACAO_AUTOMATICA = "verificar_estrutura"

def carregar_jogos_necessarios():
    """Carrega a lista de arquivos necessários para cada jogo a partir de um arquivo JSON remoto."""
    try:
        resposta = requests.get(JOGOS_NECESSARIOS_URL)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print(f"Erro ao carregar jogos necessários: {e}")
        return {}

def carregar_plugins(diretorio="plugins"):
    """Carrega todos os plugins na pasta especificada e executa o plugin de verificação automática."""
    plugins = {}
    if not os.path.exists(diretorio):
        print(f"Diretório de plugins '{diretorio}' não encontrado.")
        return plugins

    import sys
    sys.path.append(diretorio)

    for filename in os.listdir(diretorio):
        if filename.endswith(".py") and filename != "__init__.py":
            nome_plugin = filename[:-3]  # Remove ".py"
            try:
                modulo = importlib.import_module(nome_plugin)
                importlib.reload(modulo)  # Recarrega o módulo

                # Executa automaticamente o plugin de verificação de estrutura
                if nome_plugin == PLUGIN_VERIFICACAO_AUTOMATICA:
                    if hasattr(modulo, "executar"):
                        print(f"Executando verificação automática: {nome_plugin}")
                        modulo.executar()  # Executa o plugin de verificação
                # Adiciona os outros plugins ao menu conforme PLUGINS_VISIVEIS
                elif nome_plugin in PLUGINS_VISIVEIS and hasattr(modulo, "executar"):
                    plugins[nome_plugin] = modulo.executar
                    print(f"Plugin '{nome_plugin}' carregado para o menu.")
            except ImportError as e:
                print(f"Erro ao carregar o plugin '{nome_plugin}': {e}")

    return plugins

# Classe e código de `JogoWidget` continuam como antes...

class JogoWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(JogoWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.selected_game = None
        self.jogos_necessarios = carregar_jogos_necessarios()  # Carrega a lista de arquivos necessários

        # Rótulo para escolher o jogo
        self.add_widget(Label(text='Escolha o jogo:', size_hint_y=None, height=40))

        # Layout para os jogos
        self.jogos_layout = GridLayout(cols=1, size_hint_y=None)
        self.jogos_layout.bind(minimum_height=self.jogos_layout.setter('height'))

        # Adicionando ToggleButtons para cada jogo
        self.jogo_buttons = {}
        for jogo in self.jogos_necessarios.keys():
            button = ToggleButton(text=jogo, group='jogos')
            button.bind(on_press=self.on_toggle_button_press)
            self.jogos_layout.add_widget(button)
            self.jogo_buttons[jogo] = button

        self.add_widget(self.jogos_layout)

        # Botão para iniciar o jogo
        start_button = Button(text='Iniciar Jogo', size_hint_y=None, height=50)
        start_button.bind(on_press=self.iniciar_jogo)
        self.add_widget(start_button)

        # Label para status
        self.status_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.status_label)

        # Nova label para mostrar o arquivo atual sendo baixado
        self.download_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.download_label)

    # Outros métodos de JogoWidget continuam iguais...
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

# Função para ser reconhecida como um plugin
def executar():
    """Função principal do plugin que será chamada pelo sistema de plugins."""
    jogo_widget = JogoWidget()
    popup = Popup(title="Plugins", content=jogo_widget, size_hint=(0.9, 0.9))
    popup.open()
