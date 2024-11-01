# app.py

import os
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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class UpdaterApp(App):
    def build(self):
        self.title = "Launcher NPED"
        Window.size = (950, 800)  # Ajuste de tamanho para acomodar todos os elementos sem sobreposição

        # Layout principal com espaçamento e padding ajustados
        main_layout = BoxLayout(orientation='vertical', padding=[20, 60, 20, 20], spacing=20)

        # Logo na parte superior
        logo_path = resource_path("nped.png")
        if os.path.exists(logo_path):
            logo = KivyImage(source=logo_path, size_hint=(None, None), size=(150, 200))
            logo_layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None), height=200)
            logo_layout.add_widget(logo)
            main_layout.add_widget(logo_layout)

        # Layout para exibir versões
        version_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        self.current_version_label = Label(text=f"Versão do Launcher: {get_current_version()}", halign='center', valign='middle')
        self.server_version_label = Label(text=f"Versão do Servidor: {get_server_version()}", halign='center', valign='middle')
        version_layout.add_widget(self.current_version_label)
        version_layout.add_widget(self.server_version_label)

        main_layout.add_widget(version_layout)

        # Status da atualização e barra de progresso abaixo das versões
        status_progress_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=80, spacing=10)
        self.update_status_label = Label(text="", size_hint=(1, None), height=30)
        self.progress_bar = ProgressBar(max=100, size_hint=(1, None), height=30)
        status_progress_layout.add_widget(self.update_status_label)
        status_progress_layout.add_widget(self.progress_bar)
        main_layout.add_widget(status_progress_layout)

        # Widget de notícias
        self.news_widget = NewsWidget(size_hint=(1, None), height=300)
        main_layout.add_widget(self.news_widget)

        # Layout para botões na parte inferior
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, padding=[0, 0, 20, 0])

        # Botão de Menu para Plugins (à esquerda)
        plugins_button = Button(text="Menu", size_hint=(None, None), size=(120, 50))
        plugins_button.bind(on_release=self.show_plugins_popup)
        button_layout.add_widget(plugins_button)

        # Espaço para empurrar o botão "Atualizar" para o lado direito
        button_layout.add_widget(Label(size_hint=(1, 1)))

        # Botão de Atualização (à direita)
        self.update_button = Button(text="Atualizar", size_hint=(None, None), size=(120, 50), disabled=True)
        self.update_button.bind(on_press=self.on_update_button_press)
        button_layout.add_widget(self.update_button)

        main_layout.add_widget(button_layout)

        # Carregar plugins e verificar a versão do servidor
        self.plugins = carregar_plugins()
        self.check_version()

        return main_layout

    def show_plugins_popup(self, instance):
        grid_layout = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        for nome_plugin, funcao_plugin in self.plugins.items():
            btn = Button(text=nome_plugin, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.executar_plugin(btn.text))
            grid_layout.add_widget(btn)

        popup = Popup(title="Plugins Disponíveis", content=grid_layout, size_hint=(0.8, 0.8))
        popup.open()

    def check_version(self):
        current_version = get_current_version()
        server_version = get_server_version()
        self.current_version_label.text = f"Versão do Launcher: {current_version}"
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
        """Atualiza o valor da barra de progresso."""
        self.progress_bar.value = progress

    def executar_plugin(self, nome_plugin):
        if nome_plugin in self.plugins:
            self.plugins[nome_plugin]()

if __name__ == '__main__':
    UpdaterApp().run()
