#app.py v-1.3

import os
import sys
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivy.config import Config

from utils import (get_current_version, get_server_version, download_update,
                   extract_update, move_files, remove_updater_folder, update_current_version)
from news import NewsWidget
from plugins import carregar_plugins

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


class GlowingLogo(Widget):
    """Widget para criar o efeito de brilho ao redor do logo."""
    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        with self.canvas.before:
            # Adiciona um brilho azul translúcido
            Color(0, 0.8, 1, 0.5)  # Azul claro translúcido
            self.ellipse = Ellipse(size=(200, 200), pos=(self.center_x - 100, self.center_y - 100))

        self.image = Image(source=self.source, size_hint=(None, None), size=(150, 150), pos_hint={"center_x": 0.5})
        self.add_widget(self.image)

    def on_size(self, *args):
        """Atualiza a posição do brilho quando o widget for redimensionado."""
        self.ellipse.size = (200, 200)
        self.ellipse.pos = (self.center_x - 100, self.center_y - 100)


class UpdaterApp(MDApp):
    def build(self):
        # Configurar tema
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
            logo_layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None), height=250)
            logo = GlowingLogo(source=logo_path)
            logo_layout.add_widget(logo)
            main_layout.add_widget(logo_layout)

        # Versões
        version_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=40, spacing=20)
        self.current_version_label = MDLabel(
            text=f"Versão Atual: {get_current_version()}",
            halign="center",
            theme_text_color="Custom",
            text_color=(0, 1, 1, 1),
            font_style="Subtitle1"
        )
        self.server_version_label = MDLabel(
            text=f"Versão do Servidor: {get_server_version()}",
            halign="center",
            theme_text_color="Custom",
            text_color=(0, 1, 1, 1),
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
            theme_text_color="Hint",
            font_style="Body1"
        )
        self.progress_bar = MDProgressBar(value=0, size_hint=(1, None), height=20)
        status_progress_layout.add_widget(self.update_status_label)
        status_progress_layout.add_widget(self.progress_bar)
        main_layout.add_widget(status_progress_layout)

        # Widget de notícias
        self.news_widget = NewsWidget(size_hint=(1, None), height=300)
        main_layout.add_widget(self.news_widget)

        # Botões (Menu à esquerda, Atualizar à direita)
        button_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=80, padding=[20, 0, 20, 0])

        # Botão de menu (à esquerda)
        plugins_button = MDRaisedButton(
            text="Menu",
            size_hint=(None, None),
            size=(150, 50),
            md_bg_color=(0, 0.5, 1, 1),
            text_color=(1, 1, 1, 1),
            radius=[30]
        )
        plugins_button.bind(on_release=self.show_plugins_popup)
        button_layout.add_widget(plugins_button)

        # Espaço flexível entre os botões
        button_layout.add_widget(Widget(size_hint=(1, 1)))

        # Botão de atualização (à direita)
        self.update_button = MDRaisedButton(
            text="Atualizar",
            size_hint=(None, None),
            size=(150, 50),
            md_bg_color=(0, 0.8, 1, 1),
            text_color=(1, 1, 1, 1),
            radius=[30],
            disabled=True
        )
        self.update_button.bind(on_press=self.on_update_button_press)
        button_layout.add_widget(self.update_button)

        main_layout.add_widget(button_layout)

        # Carregar plugins e verificar a versão
        self.plugins = carregar_plugins()
        self.check_version()

        return main_layout

    def show_plugins_popup(self, instance):
        grid_layout = MDGridLayout(cols=2, spacing=10, padding=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        for nome_plugin, funcao_plugin in self.plugins.items():
            btn = MDRaisedButton(
                text=nome_plugin,
                size_hint=(None, None),
                size=(150, 50),
                md_bg_color=(0, 0.8, 1, 1),
                text_color=(1, 1, 1, 1),
                radius=[30]
            )
            btn.bind(on_release=lambda btn: self.executar_plugin(btn.text))
            grid_layout.add_widget(btn)

        self.dialog = MDDialog(
            title="Plugins Disponíveis",
            type="custom",
            content_cls=grid_layout,
            buttons=[
                MDRaisedButton(
                    text="Fechar",
                    on_release=lambda _: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def check_version(self):
        current_version = get_current_version()
        server_version = get_server_version()
        self.current_version_label.text = f"Versão Atual: {current_version}"
        self.server_version_label.text = f"Versão do Servidor: {server_version}"
        if current_version != server_version:
            self.update_button.disabled = False

    def on_update_button_press(self, instance):
        self.update_status_label.text = "Atualizando..."
        self.progress_bar.value = 0
        if download_update(self.update_progress):
            if extract_update():
                os.remove('atualizacao.zip')
                move_files(self.update_progress)
                remove_updater_folder()
                self.progress_bar.value = 100
                self.update_status_label.text = "Atualização concluída."
                new_version = get_server_version()
                update_current_version(new_version)
            else:
                self.update_status_label.text = "Erro ao extrair a atualização."
        else:
            self.update_status_label.text = "Erro ao baixar a atualização."

    def update_progress(self, progress):
        self.progress_bar.value = progress

    def executar_plugin(self, nome_plugin):
        if nome_plugin in self.plugins:
            self.plugins[nome_plugin]()


if __name__ == '__main__':
    UpdaterApp().run()
