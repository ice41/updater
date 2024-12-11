# app.py versão 2.4
# app.py versão 2.3

import os
import sys
import requests
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRaisedButton

# URLs para os arquivos remotos
NEWS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/news-1.2.py"
PLUGINS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/plugins.py"
UTILS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/app/utils.py"

# Desativar os provedores de entrada problemáticos
Config.set('input', 'wm_touch', 'null')
Config.set('input', 'wm_pen', 'null')
Config.set('graphics', 'multitouch_on_demand', True)

def load_remote_module(url, module_name):
    """Carrega e executa um módulo Python remoto diretamente."""
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

if utils:
    get_current_version = utils.get("get_current_version")
    get_server_version = utils.get("get_server_version")
    download_update = utils.get("download_update")
    extract_update = utils.get("extract_update")
    move_files = utils.get("move_files")
    remove_updater_folder = utils.get("remove_updater_folder")
    update_current_version = utils.get("update_current_version")

class UpdaterApp(MDApp):
    def build(self):
        self.title = "Launcher NPED"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        Window.size = (950, 800)

        main_layout = MDBoxLayout(orientation='vertical', padding=[20, 60, 20, 20], spacing=20)

        # Logo no topo
        logo_path = resource_path("nped.png")
        if os.path.exists(logo_path):
            logo_layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None), height=200)
            logo_image = KivyImage(source=logo_path, allow_stretch=True, size_hint=(None, None), size=(150, 200))
            logo_layout.add_widget(logo_image)
            main_layout.add_widget(logo_layout)

        # Versões
        version_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=40, spacing=20)
        self.current_version_label = MDLabel(
            text=f"Versão do Launcher: {get_current_version()}",
            halign="center",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )
        self.server_version_label = MDLabel(
            text=f"Versão do Servidor: {get_server_version()}",
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

        self.open_launcher_label = MDLabel(
            text="Abrir o novo Launcher",
            size_hint=(1, None),
            halign="center",
            font_style="H6",
            theme_text_color="Primary",
            opacity=0  # Inicialmente invisível
        )
        main_layout.add_widget(self.open_launcher_label)

        # Botões
        button_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=80, padding=[0, 0, 20, 0])
        plugins_button = MDRectangleFlatButton(
            text="Menu",
            size_hint=(None, None),
            size=(120, 50),
            pos_hint={"center_y": 0.5}
        )
        plugins_button.bind(on_release=self.show_plugins_popup)
        button_layout.add_widget(plugins_button)

        button_layout.add_widget(MDLabel(size_hint=(1, 1)))

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

        self.plugins = plugins.get("carregar_plugins")() if plugins else {}
        self.check_version()

        return main_layout

    def check_version(self):
        current_version = get_current_version()
        server_version = get_server_version()
        self.current_version_label.text = f"Versão do Launcher: {current_version}"
        self.server_version_label.text = f"Versão do Servidor: {server_version}"
        if current_version != server_version:
            self.update_button.disabled = False
        else:
            self.progress_bar.opacity = 0  # Oculta a barra se não houver atualizações

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

                self.open_launcher_label.opacity = 1  # Mostra a nova label
                new_version = get_server_version()
                update_current_version(new_version)
            else:
                self.update_status_label.text = "Erro ao extrair a atualização."

    def update_progress(self, progress):
        self.progress_bar.value = progress

    def show_plugins_popup(self, instance):
        grid_layout = MDGridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        for nome_plugin, funcao_plugin in self.plugins.items():
            btn = MDRectangleFlatButton(
                text=nome_plugin, size_hint_y=None, height=44
            )
            btn.bind(on_release=lambda btn: self.executar_plugin(btn.text))
            grid_layout.add_widget(btn)

        self.dialog = MDDialog(
            title="Plugins Disponíveis",
            type="custom",
            content_cls=grid_layout,
            buttons=[MDRaisedButton(text="Fechar", on_release=lambda _: self.dialog.dismiss())]
        )
        self.dialog.open()

    def executar_plugin(self, nome_plugin):
        if nome_plugin in self.plugins:
            self.plugins[nome_plugin]()


if __name__ == '__main__':
    UpdaterApp().run()
