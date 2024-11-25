# app.py versão 2.5
# app.py com novo design aplicado
import os
import sys
import requests
from kivymd.app import MDApp
from kivy.lang import Builder
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

# Design em formato KV (com base na imagem fornecida)
KV = '''
BoxLayout:
    orientation: "vertical"
    padding: [20, 60, 20, 20]
    spacing: 20
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1  # Fundo preto
        Rectangle:
            pos: self.pos
            size: self.size

    # Imagem do topo
    Image:
        source: "pharaoh_image.png"  # Substitua pela imagem do faraó
        size_hint: None, None
        size: 150, 150
        pos_hint: {"center_x": 0.5}

    # Texto de versão
    MDLabel:
        text: app.get_versions()
        halign: "center"
        theme_text_color: "Custom"
        text_color: 0.8, 0.8, 0.8, 1
        font_size: "18sp"

    # Notícias
    MDBoxLayout:
        orientation: "vertical"
        padding: 10
        md_bg_color: 0.1, 0.1, 0.3, 1
        radius: [20, 20, 20, 20]
        size_hint_y: None
        height: 200
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
            text: app.get_news()
            markup: True  # Ativa o suporte a BBCode para o texto
            halign: "left"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1

    # Botões
    MDBoxLayout:
        orientation: "horizontal"
        spacing: 10
        size_hint_y: None
        height: 50

        MDRaisedButton:
            text: "Menu"
            md_bg_color: 0, 0.4, 1, 1
            on_release: app.show_plugins_popup()

        MDRaisedButton:
            text: "Atualizar"
            md_bg_color: 0.2, 0.8, 0.2, 1
            on_press: app.on_update_button_press()
'''

class UpdaterApp(MDApp):
    def build(self):
        # Configuração inicial
        self.title = "Launcher NPED"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Window.size = (950, 800)

        # Renderizar o layout do KV
        return Builder.load_string(KV)

    def get_versions(self):
        """Obtém as versões do launcher e servidor."""
        current_version = get_current_version() if get_current_version else "N/A"
        server_version = get_server_version() if get_server_version else "N/A"
        return f"Versão atual: {current_version} | Servidor: {server_version}"

    def get_news(self):
    """Obtém notícias do arquivo JSON hospedado no GitHub e retorna como string."""
    url = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/news/news.json"

    try:
        # Faz o download do JSON
        response = requests.get(url)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        news_data = response.json()  # Converte para um objeto Python (lista de dicionários)

        # Constrói uma string para exibir no label
        news_text = ""
        for item in news_data:
            title = item.get("title", "Sem título")
            description = item.get("description", "Sem descrição")
            news_text += f"[b]{title}[/b]\n{description}\n\n"  # Exemplo de formatação usando BBCode

        return news_text.strip()  # Remove espaços ou quebras extras no final
    except Exception as e:
        print("Erro ao obter notícias:", e)
        return "Erro ao carregar notícias."

    def on_update_button_press(self):
        """Lógica para o botão de atualização."""
        print("Iniciando atualização...")
        # Adicione aqui a lógica de atualização (baixa, extrai e aplica arquivos)

    def show_plugins_popup(self):
        """Exibe o menu de plugins."""
        print("Abrindo menu de plugins...")
        # Aqui você pode implementar um diálogo ou menu com os plugins disponíveis

if __name__ == '__main__':
    UpdaterApp().run()
