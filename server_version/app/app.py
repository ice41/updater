#app.py

import os
import sys
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivy.config import Config
import requests

# URLs dos módulos no GitHub
UTILS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/utils.py"
NEWS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/news.py"
PLUGINS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/plugins.py"

# Função para carregar módulos diretamente do GitHub
def carregar_modulo(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Garante que o download foi bem-sucedido
        codigo = response.text
        namespace = {}
        exec(codigo, namespace)  # Executa o código no namespace
        return namespace
    except requests.RequestException as e:
        print(f"Erro ao carregar o módulo de {url}: {e}")
        return None

# Carregar módulos
utils = carregar_modulo(UTILS_URL)
news = carregar_modulo(NEWS_URL)
plugins = carregar_modulo(PLUGINS_URL)

# Desativar os provedores de entrada problemáticos
Config.set('input', 'wm_touch', 'null')
Config.set('input', 'wm_pen', 'null')
Config.set('graphics', 'multitouch_on_demand', True)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class UpdaterApp(MDApp):
    def build(self):
        # Configurar tema escuro
        self.title = "Launcher NPED"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        Window.size = (950, 800)

        # Layout principal
        main_layout = MDBoxLayout(orientation='vertical', padding=[20, 60, 20, 20], spacing=20)

        # Logo no topo
        logo_path = resource_path("nped.png")
        if os.path.exists(logo_path):
            logo_layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None), height=200)
            main_layout.add_widget(logo_layout)

        # Versões
        version_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=40, spacing=20)
        self.current_version_label = MDLabel(
            text=f"Versão do Launcher: {utils['get_current_version']()}",
            halign="center",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )
        self.server_version_label = MDLabel(
            text=f"Versão do Servidor: {utils['get_server_version']()}",
            halign="center",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )
        version_layout.add_widget(self.current_version_label)
        version_layout.add_widget(self.server_version_label)
        main_layout.add_widget(version_layout)

        # Status da atualização e barra de progresso
        status_progress_layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), height=80, spacing=10)
        self.update_status_label = MDLabel(
            text="",
            size_hint=(1, None),
            height=30,
            halign="center",
            theme_text_color="Secondary"
        )
        self.progress_bar = MDProgressBar(value=0, size_hint=(1, None), height=20)
        status_progress_layout.add_widget(self.update_status_label)
        status_progress_layout.add_widget(self.progress_bar)
        main_layout.add_widget(status_progress_layout)

        # Widget de notícias
        self.news_widget = news['NewsWidget'](size_hint=(1, None), height=300)
        main_layout.add_widget(self.news_widget)

        # Botões
        button_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=80, padding=[0, 0, 20, 0])

        # Botão de menu (à esquerda)
        plugins_button = MDRectangleFlatButton(
            text="Menu",
            size_hint=(None, None),
            size=(120, 50),
            pos_hint={"center_y": 0.5}
        )
        plugins_button.bind(on_release=self.show_plugins_popup)
        button_layout.add_widget(plugins_button)

        # Espaço para empurrar o botão de "Atualizar"
        button_layout.add_widget(MDLabel(size_hint=(1, 1)))

        # Botão de atualização
        self.update_button = MDRaisedButton(
            text="Atualizar",
            size_hint=(None, None),
            size=(120, 50),
            pos_hint={"center_y": 0.5},
            disabled=True
        )
        self.update_button.bind(on_press=self.on_update_button_press)
        button_layout.add_widget(self.update_button)

        main_layout.add_widget(button_layout)

        # Carregar plugins e verificar a versão
        self.plugins = plugins['carregar_plugins']()
        self.check_version()

        return main_layout

    def show_plugins_popup(self, instance):
        # Popup para mostrar plugins
        pass

    def check_version(self):
        # Verifica e atualiza versões
        pass

    def on_update_button_press(self, instance):
        # Atualizar aplicativo
        pass


if __name__ == '__main__':
    UpdaterApp().run()

