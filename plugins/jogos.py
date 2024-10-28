import os
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

def carregar_jogos_necessarios():
    """Carrega a lista de arquivos necessários para cada jogo a partir de um arquivo JSON remoto."""
    try:
        resposta = requests.get(JOGOS_NECESSARIOS_URL)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print(f"Erro ao carregar jogos necessários: {e}")
        return {}

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

    def on_toggle_button_press(self, instance):
        for button in self.jogo_buttons.values():
            if button != instance:
                button.state = 'normal'
        self.selected_game = instance.text if instance.state == 'down' else None

    def iniciar_jogo(self, instance):
        if self.selected_game:
            jogo_selecionado = self.selected_game
            caminho_jogos = os.path.join("jogos", jogo_selecionado)

            if os.path.exists(caminho_jogos):
                arquivos_faltando = self.verificar_arquivos(caminho_jogos, self.jogos_necessarios.get(jogo_selecionado, []))

                if not arquivos_faltando:
                    executavel = os.path.join(caminho_jogos, "abrir.bat")
                    if os.path.exists(executavel):
                        self.status_label.text = f"Iniciando o jogo: {jogo_selecionado}..."
                        os.startfile(executavel)
                    else:
                        self.show_popup("Erro", f"Executável não encontrado em {caminho_jogos}.")
                else:
                    self.status_label.text = "Arquivos faltando, iniciando download..."
                    # Iniciar o download dos arquivos
                    self.baixar_arquivos(jogo_selecionado, arquivos_faltando)
            else:
                self.show_popup("Erro", f"A pasta {caminho_jogos} não existe.")
        else:
            self.show_popup("Aviso", "Por favor, selecione um jogo.")

    def verificar_arquivos(self, caminho_jogos, arquivos_necessarios):
        faltando = []
        for arquivo in arquivos_necessarios:
            self.status_label.text = f"Verificando: {arquivo}"
            self.download_label.text = f"Verificando: {arquivo}"
            if not os.path.exists(os.path.join(caminho_jogos, arquivo)):
                faltando.append(arquivo)
        return faltando

    def baixar_arquivos(self, jogo, arquivos_faltando):
        url_base = f"http://158.178.197.238/jogos/{jogo}/"
        self.download_next_file(url_base, arquivos_faltando)

    def download_next_file(self, url_base, arquivos_faltando):
        if arquivos_faltando:
            arquivo = arquivos_faltando.pop(0)
            url_arquivo = os.path.join(url_base, arquivo)
            caminho_destino = os.path.join("jogos", self.selected_game, arquivo)
            self.download_label.text = f"Baixando: {arquivo}"
            os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

            try:
                resposta = requests.get(url_arquivo)
                resposta.raise_for_status()

                with open(caminho_destino, "wb") as f:
                    f.write(resposta.content)

                self.status_label.text = f"Download: {arquivo} com sucesso!"
                self.download_label.text = ''

            except Exception as e:
                self.show_popup("Erro", f"Falha ao baixar {arquivo}")

            Clock.schedule_once(lambda dt: self.download_next_file(url_base, arquivos_faltando), 1)
        else:
            self.status_label.text = "Todos os arquivos foram baixados."

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

# Função para ser reconhecida como um plugin
def executar():
    """Função principal do plugin que será chamada pelo sistema de plugins."""
    jogo_widget = JogoWidget()
    popup = Popup(title="Jogos", content=jogo_widget, size_hint=(0.9, 0.9))
    popup.open()
