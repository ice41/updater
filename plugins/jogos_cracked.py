import os
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from threading import Thread
from extractor import Extractor

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

        self.add_widget(Label(text='Escolha o jogo:', size_hint_y=None, height=40))
        self.jogos_layout = GridLayout(cols=1, size_hint_y=None)
        self.jogos_layout.bind(minimum_height=self.jogos_layout.setter('height'))

        self.jogo_buttons = {}
        for jogo in self.jogos_necessarios.keys():
            button = ToggleButton(text=jogo, group='jogos')
            button.bind(on_press=self.on_toggle_button_press)
            self.jogos_layout.add_widget(button)
            self.jogo_buttons[jogo] = button

        self.add_widget(self.jogos_layout)

        self.start_button = Button(text='Iniciar Jogo', size_hint_y=None, height=50)
        self.start_button.bind(on_press=self.iniciar_jogo)
        self.add_widget(self.start_button)

        self.uninstall_button = Button(text='Desinstalar Jogo', size_hint_y=None, height=50, disabled=True)
        self.uninstall_button.bind(on_press=self.desinstalar_jogo)
        self.add_widget(self.uninstall_button)

        self.status_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.status_label)

        self.download_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.download_label)

        self.remaining_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.remaining_label)

    def on_toggle_button_press(self, instance):
        for button in self.jogo_buttons.values():
            if button != instance:
                button.state = 'normal'
        self.selected_game = instance.text if instance.state == 'down' else None
        self.atualizar_botoes()

    def atualizar_botoes(self):
        if self.selected_game:
            caminho_jogo = os.path.join("jogos", self.selected_game)
            if os.path.exists(caminho_jogo):
                arquivos_faltando = self.verificar_arquivos(caminho_jogo, self.jogos_necessarios.get(self.selected_game, []))
                if not arquivos_faltando:
                    self.start_button.text = "Iniciar Jogo"
                    self.start_button.disabled = False
                    self.uninstall_button.disabled = False
                else:
                    self.start_button.text = "Instalar Jogo"
                    self.start_button.disabled = False
                    self.uninstall_button.disabled = True
            else:
                self.start_button.text = "Instalar Jogo"
                self.start_button.disabled = False
                self.uninstall_button.disabled = True
        else:
            self.start_button.text = "Iniciar Jogo"
            self.start_button.disabled = True
            self.uninstall_button.disabled = True

    def iniciar_jogo(self, instance):
        if self.selected_game:
            jogo_selecionado = self.selected_game
            caminho_jogos = os.path.join("jogos", jogo_selecionado)

            if os.path.exists(caminho_jogos):
                arquivos_faltando = self.verificar_arquivos(caminho_jogos, self.jogos_necessarios.get(jogo_selecionado, []))

                if not arquivos_faltando:
                    executavel = os.path.join(caminho_jogos, "iniciar.bat")
                    if os.path.exists(executavel):
                        self.status_label.text = f"Iniciando o jogo: {jogo_selecionado}..."
                        os.startfile(executavel)
                    else:
                        self.show_popup("Erro", f"Executável não encontrado em {caminho_jogos}.")
                else:
                    self.status_label.text = "Arquivos faltando, iniciando download..."
                    self.baixar_arquivos(jogo_selecionado, arquivos_faltando)
            else:
                self.baixar_arquivos(jogo_selecionado, self.jogos_necessarios.get(jogo_selecionado, []))
        else:
            self.show_popup("Aviso", "Por favor, selecione um jogo.")

    def verificar_arquivos(self, caminho_jogos, arquivos_necessarios):
        faltando = []
        for arquivo in arquivos_necessarios:
            if not os.path.exists(os.path.join(caminho_jogos, arquivo)):
                faltando.append(arquivo)
        return faltando

    def baixar_arquivos(self, jogo, arquivos_faltando):
        url_base = f"http://158.178.197.238/jogos/{jogo}/"
        Thread(target=self.download_next_file, args=(url_base, arquivos_faltando)).start()

    def download_next_file(self, url_base, arquivos_faltando):
        if arquivos_faltando:
            arquivo = arquivos_faltando.pop(0)
            url_arquivo = os.path.join(url_base, arquivo)
            caminho_destino = os.path.join("jogos", self.selected_game, arquivo)

            self.download_label.text = f"Baixando: {arquivo}"
            os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

            try:
                with requests.get(url_arquivo, stream=True) as resposta:
                    resposta.raise_for_status()
                    tamanho_total = int(resposta.headers.get('Content-Length', 0))
                    tamanho_baixado = 0

                    with open(caminho_destino, "wb") as f:
                        for chunk in resposta.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                                tamanho_baixado += len(chunk)
                                restante_mb = (tamanho_total - tamanho_baixado) / (1024 * 1024)

                                # Atualiza a label restante com total e restante
                                self.update_download_label(restante_mb, tamanho_total / (1024 * 1024))

                self.status_label.text = f"Download {arquivo} concluído."
            except Exception as e:
                self.show_popup("Erro", f"Falha ao baixar {arquivo}")

            self.download_next_file(url_base, arquivos_faltando)
        else:
            self.status_label.text = "Todos os arquivos foram baixados."
            Extractor.extrair_arquivos()
            self.atualizar_botoes()

    def update_download_label(self, restante_mb, total_mb):
        def atualizar_label(dt):
            self.remaining_label.text = f"Restam: {restante_mb:.2f} MB de: {total_mb:.2f} MB"
        if restante_mb == 0:
        # Download concluído, iniciar o extractor
        print("Download completo. Executando o Extractor...")
        try:
            Extractor.extrair_arquivos()
            print("Extração dos arquivos concluída com sucesso.")

        except Exception as ex:
            print(f"Erro ao extrair arquivos: {str(ex)}")
        self.update_status_label.text = "Atualização concluída."
        
        Clock.schedule_once(atualizar_label)

    def desinstalar_jogo(self, instance):
        if self.selected_game:
            caminho_jogo = os.path.join("jogos", self.selected_game)
            if os.path.exists(caminho_jogo):
                for root, dirs, files in os.walk(caminho_jogo, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))

                os.rmdir(caminho_jogo)
                self.status_label.text = f"Jogo {self.selected_game} desinstalado com sucesso."
                self.atualizar_botoes()
            else:
                self.show_popup("Erro", "Jogo não encontrado para desinstalar.")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

def executar():
    jogo_widget = JogoWidget()
    popup = Popup(title="Jogos Cracked", content=jogo_widget, size_hint=(0.9, 0.9))
    popup.open()
