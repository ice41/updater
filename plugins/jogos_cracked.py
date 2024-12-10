import os
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import subprocess

# URL do JSON com os arquivos necessários para cada jogo
JOGOS_NECESSARIOS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/jogos_necessarios.json"

# Mapeamento de nomes de arquivos iniciais para cada jogo
ARQUIVOS_INICIAIS = {
    "SoulMask": "jogos/soulmask/WS/Content/Paks/WS-WindowsNoEditor.7z.001",
    "FirstDward": "jogos/firstdwarf/Content/Paks/FirstDwarf-Windows.7z.001"
}

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

        # Botões para ações
        self.extract_button = Button(text='Extrair Arquivos', size_hint_y=None, height=50, disabled=True)
        self.extract_button.bind(on_press=self.extrair_arquivos)
        self.add_widget(self.extract_button)

        self.start_button = Button(text='Iniciar Jogo', size_hint_y=None, height=50, disabled=True)
        self.start_button.bind(on_press=self.iniciar_jogo)
        self.add_widget(self.start_button)

        self.uninstall_button = Button(text='Desinstalar Jogo', size_hint_y=None, height=50, disabled=True)
        self.uninstall_button.bind(on_press=self.desinstalar_jogo)
        self.add_widget(self.uninstall_button)

        # Label para status
        self.status_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.status_label)

        # Label para mostrar o arquivo atual sendo baixado
        self.download_label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.download_label)

    def on_toggle_button_press(self, instance):
        """Marca o jogo selecionado quando o botão é pressionado."""
        for button in self.jogo_buttons.values():
            if button != instance:
                button.state = 'normal'
        self.selected_game = instance.text if instance.state == 'down' else None
        self.atualizar_botoes()

    def atualizar_botoes(self):
        """Atualiza os botões com base no estado do jogo selecionado."""
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

                # Habilita o botão de extração se arquivos .7z.001 forem encontrados
                primeiro_arquivo = os.path.join(caminho_jogo, ARQUIVOS_INICIAIS.get(self.selected_game, ""))
                self.extract_button.disabled = not os.path.exists(primeiro_arquivo)
            else:
                self.start_button.text = "Instalar Jogo"
                self.start_button.disabled = False
                self.uninstall_button.disabled = True
                self.extract_button.disabled = True
        else:
            self.start_button.text = "Iniciar Jogo"
            self.start_button.disabled = True
            self.uninstall_button.disabled = True
            self.extract_button.disabled = True

    def iniciar_jogo(self, instance):
        """Inicia ou instala o jogo selecionado, dependendo do estado."""
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
        """Verifica se todos os arquivos necessários estão presentes."""
        faltando = []
        for arquivo in arquivos_necessarios:
            if not os.path.exists(os.path.join(caminho_jogos, arquivo)):
                faltando.append(arquivo)
        return faltando

    def extrair_arquivos(self, instance):
        """Extrai os arquivos segmentados (.7z.001) se existirem."""
        if self.selected_game:
            caminho_jogo = os.path.join("jogos", self.selected_game)
            primeiro_arquivo = os.path.join(caminho_jogo, ARQUIVOS_INICIAIS.get(self.selected_game, ""))

            if os.path.exists(primeiro_arquivo):
                self.status_label.text = "Extraindo arquivos..."
                comando = ["7z", "x", primeiro_arquivo, f"-o{caminho_jogo}"]

                try:
                    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    if resultado.returncode == 0:
                        self.status_label.text = "Arquivos extraídos com sucesso!"
                    else:
                        self.status_label.text = f"Falha na extração dos arquivos. Código de erro: {resultado.returncode}"
                        print("Erro:", resultado.stderr)
                except FileNotFoundError:
                    self.show_popup("Erro", "O programa 7z não foi encontrado. Certifique-se de que está instalado e acessível.")
            else:
                self.show_popup("Erro", "Arquivo base para extração não encontrado.")

    def baixar_arquivos(self, jogo, arquivos_faltando):
        """Inicia o processo de download dos arquivos faltando."""
        url_base = f"http://158.178.197.238/jogos/{jogo}/"
        self.download_next_file(url_base, arquivos_faltando)

    def download_next_file(self, url_base, arquivos_faltando):
        """Baixa o próximo arquivo da lista até que todos estejam baixados."""
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

                self.status_label.text = f"Download: {arquivo} concluído."
                self.download_label.text = ''
            except Exception as e:
                self.show_popup("Erro", f"Falha ao baixar {arquivo}")

            Clock.schedule_once(lambda dt: self.download_next_file(url_base, arquivos_faltando), 1)
        else:
            self.status_label.text = "Todos os arquivos foram baixados."
            self.atualizar_botoes()

    def desinstalar_jogo(self, instance):
        """Desinstala o jogo selecionado, removendo seus arquivos."""
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
        """Exibe um popup com uma mensagem de erro ou aviso."""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

def executar():
    """Função principal do plugin que será chamada pelo sistema de ."""
    jogo_widget = JogoWidget()
    popup = Popup(title="Jogos Cracked", content=jogo_widget, size_hint=(0.9, 0.9))
    popup.open()

def encontrar_7z():
    """Tenta localizar o executável do 7-Zip no sistema."""
    caminhos_possiveis = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe"
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            return caminho
    return "7z"  # Retorna o comando genérico, se não encontrar nos caminhos padrão.

def extrair_arquivos(self, instance):
    """Extrai os arquivos segmentados (.7z.001) se existirem."""
    if self.selected_game:
        caminho_jogo = os.path.join("jogos", self.selected_game)
        primeiro_arquivo = os.path.join(caminho_jogo, ARQUIVOS_INICIAIS.get(self.selected_game, ""))

        if os.path.exists(primeiro_arquivo):
            self.status_label.text = "Extraindo arquivos..."
            caminho_7z = encontrar_7z()
            comando = [caminho_7z, "x", primeiro_arquivo, f"-o{caminho_jogo}"]

            try:
                resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if resultado.returncode == 0:
                    self.status_label.text = "Arquivos extraídos com sucesso!"
                else:
                    self.status_label.text = f"Falha na extração dos arquivos. Código de erro: {resultado.returncode}"
                    print("Erro:", resultado.stderr)
            except FileNotFoundError:
                self.show_popup("Erro", "O programa 7z não foi encontrado. Certifique-se de que está instalado e acessível.")
        else:
            self.show_popup("Erro", "Arquivo base para extração não encontrado.")
