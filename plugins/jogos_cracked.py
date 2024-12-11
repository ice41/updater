import os
import zipfile
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

# URL do JSON com os arquivos necessários para cada jogo
JOGOS_NECESSARIOS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/server_version/jogos_necessarios.json"

# Definições específicas para cada jogo
JOGOS_CONFIG = {
    "soulmask": {
        "pak": "WS-WindowsNoEditor.pak",
        "diretorio_pak": "jogos/soulmask/ws/Content/Paks",
        "executavel": "jogos/soulmask/iniciar.bat",
        "fragmentos_zip": "WS-WindowsNoEditor.zip"
    },
    "firstdwarf": {
        "pak": "FirstDwarf-Windows.pak",
        "diretorio_pak": "jogos/firstdwarf/Content/Paks",
        "executavel": "jogos/firstdwarf/iniciar.bat",
        "fragmentos_zip": "FirstDwarf-Windows.zip"
    }
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

def encontrar_fragmentos(diretorio, nome_base):
    """Encontra todos os fragmentos de um arquivo ZIP no diretório especificado."""
    return sorted(
        [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.startswith(nome_base) and f.endswith(".zip.001")],
        key=lambda x: x.lower()
    )

def juntar_fragmentos(fragmentos, arquivo_final):
    """Une os fragmentos de um arquivo ZIP em um único arquivo."""
    try:
        with open(arquivo_final, "wb") as f_out:
            for fragmento in fragmentos:
                with open(fragmento, "rb") as f_in:
                    f_out.write(f_in.read())
        return True
    except Exception as e:
        print(f"Erro ao juntar fragmentos: {e}")
        return False

def extrair_zip(arquivo_zip, destino):
    """Extrai o conteúdo de um arquivo ZIP para o destino especificado."""
    try:
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            zip_ref.extractall(destino)
        return True
    except zipfile.BadZipFile as e:
        print(f"Erro ao extrair ZIP: {e}")
        return False

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
        for jogo in JOGOS_CONFIG.keys():
            button = ToggleButton(text=jogo, group='jogos')
            button.bind(on_press=self.on_toggle_button_press)
            self.jogos_layout.add_widget(button)
            self.jogo_buttons[jogo] = button

        self.add_widget(self.jogos_layout)

        # Botões para ações
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
            config = JOGOS_CONFIG[self.selected_game]
            caminho_pak = os.path.join(config["diretorio_pak"], config["pak"])
            if os.path.exists(caminho_pak):
                self.start_button.text = "Iniciar Jogo"
            else:
                self.start_button.text = "Preparar Jogo"
            self.start_button.disabled = False
            self.uninstall_button.disabled = not os.path.exists(config["diretorio_pak"])
        else:
            self.start_button.text = "Iniciar Jogo"
            self.start_button.disabled = True
            self.uninstall_button.disabled = True

    def iniciar_jogo(self, instance):
        """Prepara ou inicia o jogo selecionado, dependendo do estado."""
        if self.selected_game:
            jogo_selecionado = self.selected_game
            config = JOGOS_CONFIG[jogo_selecionado]
            caminho_pak = os.path.join(config["diretorio_pak"], config["pak"])

            if os.path.exists(caminho_pak):
                executavel = config["executavel"]
                if os.path.exists(executavel):
                    self.status_label.text = f"Iniciando o jogo: {jogo_selecionado}..."
                    os.startfile(executavel)
                else:
                    self.show_popup("Erro", f"Executável não encontrado em {executavel}.")
            else:
                self.status_label.text = "Preparando o jogo..."
                self.preparar_jogo(jogo_selecionado)
        else:
            self.show_popup("Aviso", "Por favor, selecione um jogo.")

    def preparar_jogo(self, jogo):
        """Descompacta os arquivos fragmentados e cria o arquivo .pak."""
        config = JOGOS_CONFIG[jogo]
        caminho_diretorio = os.path.dirname(config["diretorio_pak"])
        nome_base = config["fragmentos_zip"]
        fragmentos = encontrar_fragmentos(caminho_diretorio, nome_base)

        if not fragmentos:
            self.show_popup("Erro", "Nenhum arquivo ZIP fragmentado encontrado para preparar o jogo.")
            return

        zip_final = os.path.join(caminho_diretorio, f"{nome_base}.zip")
        if juntar_fragmentos(fragmentos, zip_final):
            if extrair_zip(zip_final, caminho_diretorio):
                self.status_label.text = "Jogo preparado com sucesso."
                os.remove(zip_final)
                for frag in fragmentos:
                    os.remove(frag)
                self.atualizar_botoes()
            else:
                self.show_popup("Erro", "Falha ao extrair o arquivo ZIP final.")
        else:
            self.show_popup("Erro", "Falha ao juntar os fragmentos do arquivo ZIP.")

    def desinstalar_jogo(self, instance):
        """Desinstala o jogo selecionado, removendo seus arquivos."""
        if self.selected_game:
            config = JOGOS_CONFIG[self.selected_game]
            caminho_diretorio = config["diretorio_pak"]
            if os.path.exists(caminho_diretorio):
                for root, dirs, files in os.walk(caminho_diretorio, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(caminho_diretorio)
                self.status_label.text = f"Jogo {self.selected_game} desinstalado com sucesso."
                self.atualizar_botoes()
            else:
                self.show_popup("Erro", "Jogo não encontrado para desinstalar.")

    def show_popup(self, title, message):
        """Exibe um popup com uma mensagem de erro ou aviso."""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()
 def verificar_arquivos(self, caminho_jogos, arquivos_necessarios):
        """Verifica se todos os arquivos necessários estão presentes."""
        faltando = []
        for arquivo in arquivos_necessarios:
            # self.status_label.text = f"Verificando: {arquivo}"
            # self.download_label.text = f"Verificando: {arquivo}"
            if not os.path.exists(os.path.join(caminho_jogos, arquivo)):
                faltando.append(arquivo)
        return faltando

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

def executar():
    """Função principal do plugin que será chamada pelo sistema de ."""
    jogo_widget = JogoWidget()
    popup = Popup(title="Jogos Cracked", content=jogo_widget, size_hint=(0.9, 0.9))
    popup.open()
