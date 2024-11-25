# app.py versão 2.4 (com design integrado)
import os
import sys
import requests
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.config import Config

# URLs para os arquivos remotos
NEWS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/news.py"
PLUGINS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/plugins.py"
UTILS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/utils.py"

# Configurações gráficas
Config.set('input', 'wm_touch', 'null')
Config.set('input', 'wm_pen', 'null')
Config.set('graphics', 'multitouch_on_demand', True)

# Carregar módulos remotos
def load_remote_module(url, module_name):
    try:
        response = requests.get(url)
        response.raise_for_status()
        module_code = response.text
        module = {}
        exec(module_code, module)
        print(f"Carregado: {module_name}")
        return module
    except requests.RequestException as e:
        print(f"Erro ao carregar {module_name} de {url}: {e}")
        return None

# Carregar os módulos necessários dinamicamente
news = load_remote_module(NEWS_URL, "news")
plugins = load_remote_module(PLUGINS_URL, "plugins")
utils = load_remote_module(UTILS_URL, "utils")

# Funções utilitárias carregadas do módulo utils
if utils:
    get_current_version = utils.get("get_current_version")
    get_server_version = utils.get("get_server_version")
    download_update = utils.get("download_update")
    extract_update = utils.get("extract_update")
    move_files = utils.get("move_files")
    remove_updater_folder = utils.get("remove_updater_folder")
    update_current_version = utils.get("update_current_version")

# Método para buscar recursos locais ou empacotados
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Design em formato KV (substituindo o layout principal)
KV = '''
BoxLayout:
    orientation: "vertical"
    padding: 20
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1  # Cor de fundo (preto)
        Rectangle:
            pos: self.pos
            size: self.size

    # Imagem do topo
    Image:
        source: "pharaoh_image.png"  # Substitua pelo seu arquivo
        size_hint: None, None
        size: 150, 150
        pos_hint: {"center_x": 0.5}

    # Texto de versão
    MDLabel:
        text: "Versão do Launcher: 0.0.1 | Servidor: 0.0.1"
        halign: "center"
        theme_text_color: "Custom"
        text_color: 0.8, 0.8, 0.8, 1
        font_size: "18sp"

    # Notícias
    MDBoxLayout:
        orientation: "vertical"
        padding: 10
        md_bg_color: 0, 0, 0.2, 1
        radius: [20, 20, 20, 20]
        size_hint_y: None
        height: 150
        pos_hint: {"center_x": 0.5}
        spacing: 10

        MDLabel:
            text: "[b]Notícias[/b]"
            halign: "center"
            markup: True
            theme_text_color: "Custom"
            text_color: 0, 0.6, 1, 1
            font_size: "22sp"

        MDLabel:
            text: "Manutenção agendada para 20/11/2024.\\nNova atualização disponível com correções de bugs!\\nEvento especial no fim de semana."
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_size: "16sp"

    # Botões
    MDBoxLayout:
        orientation: "horizontal"
        spacing: 10
        size_hint_y: None
        height: 50
        padding: [10, 0, 10, 0]

        MDRaisedButton:
            text: "MENU"
            md_bg_color: 0, 0.4, 1, 1
            size_hint_x: 0.5
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "ATUALIZAR"
            md_bg_color: 0.5, 0.5, 0.5, 1
            size_hint_x: 0.5
            pos_hint: {"center_x": 0.5}"
'''

class UpdaterApp(MDApp):
    def build(self):
        # Configurar tema escuro
        self.title = "Launcher NPED"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Window.size = (950, 800)

        # Renderizar o layout do KV
        return Builder.load_string(KV)

if __name__ == '__main__':
    UpdaterApp().run()
