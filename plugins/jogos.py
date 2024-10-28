import os
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock  # Importar para agendar atualizações

# Defina os arquivos necessários para cada jogo
jogos_necessarios = {
    "firstdwarf": ["FirstDwarf.exe",
                   "Engine/Binaries/ThirdParty/DbgHelp/dbghelp.dll",
                   "Engine/Binaries/ThirdParty/MsQuic/v220/win64/msquic.dll",
                   "Engine/Binaries/ThirdParty/NVIDIA/NVaftermath/Win64/GFSDK_Aftermath_Lib.x64.dll",
                   "Engine/Binaries/ThirdParty/Ogg/Win64/VS2015/libogg_64.dll",
                   "Engine/Binaries/ThirdParty/Steamworks/Steamv157/Win64/steam_api64.dll",
                   "Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/libvorbisfile_64.dll",
                   "Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/libvorbis_64.dll",
                   "Engine/Binaries/ThirdParty/Windows/XAudio2_9/x64/xaudio2_9redist.dll",
                   "Engine/Binaries/Win64/CrashReportClient.exe",
                   "Engine/Binaries/Win64/tbb.dll",
                   "Engine/Binaries/Win64/tbbmalloc.dll",
                   "Engine/Content/Renderer/TessellationTable.bin",
                   "Engine/Content/Slate/Cursor/invisible.cur",
                   "Engine/Content/SlateDebug/Fonts/LastResort.tps",
                   "Engine/Content/SlateDebug/Fonts/LastResort.ttf",
                   "Engine/Programs/CrashReportClient/Content/Paks/CrashReportClient.pak",
                   "FirstDwarf/Binaries/Win64/FirstDwarf-Win64-Shipping.exe",
                   "FirstDwarf/Binaries/Win64/OpenImageDenoise.dll",
                   "FirstDwarf/Binaries/Win64/tbb.dll",
                   "FirstDwarf/Binaries/Win64/tbb12.dll",
                   "FirstDwarf/Binaries/Win64/tbbmalloc.dll",
                   "FirstDwarf/Binaries/Win64/D3D12/D3D12Core.dll",
                   "FirstDwarf/Binaries/Win64/D3D12/d3d12SDKLayers.dll",
                   "FirstDwarf/Content/Movies/Assigning_and_unlocking_Skills.bk2",
                   "FirstDwarf/Content/Movies/Assigning_and_unlocking_Skills.uasset",
                   "FirstDwarf/Content/Movies/Assigning_and_unlocking_Skills_Tex.uasset",
                   "FirstDwarf/Content/Movies/Combo_Tutorial.bk2",
                   "FirstDwarf/Content/Movies/Combo_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/Combo_Tutorial_Tex.uasset",
                   "FirstDwarf/Content/Movies/gameplay.bk2",
                   "FirstDwarf/Content/Movies/gameplay.uasset",
                   "FirstDwarf/Content/Movies/intro.bk2",
                   "FirstDwarf/Content/Movies/intro.uasset",
                   "FirstDwarf/Content/Movies/Jetpack_Tutorial.bk2",
                   "FirstDwarf/Content/Movies/Jetpack_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/Jetpack_Tutorial_Tex.uasset",
                   "FirstDwarf/Content/Movies/Loading4Loop.bk2",
                   "FirstDwarf/Content/Movies/Loading4Loop.uasset",
                   "FirstDwarf/Content/Movies/logos.bk2",
                   "FirstDwarf/Content/Movies/logos.uasset",
                   "FirstDwarf/Content/Movies/M_Assigning_and_unlocking_Skills_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/M_Combo_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/M_Jetpack_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/M_RisingSettlement_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/M_SwitchingCharacters_Tutorial.uasset",
                   "FirstDwarf/Content/Movies/Rising_Settlement.bk2",
                   "FirstDwarf/Content/Movies/Rising_Settlement.uasset",
                   "FirstDwarf/Content/Movies/Rising_Settlement_Tex.uasset",
                   "FirstDwarf/Content/Movies/Switching_Characters.bk2",
                   "FirstDwarf/Content/Movies/Switching_Characters.uasset",
                   "FirstDwarf/Content/Movies/Switching_Characters_Tex.uasset",
                   "FirstDwarf/Content/Paks/FirstDwarf-Windows.pak",
                   "FirstDwarf/Content/Splash/Splash.bmp",
                   "FirstDwarf/Plugins/DLSS/Binaries/ThirdParty/Win64/nvngx_dlss.dll",
                   "FirstDwarf/Plugins/XeSS/Binaries/ThirdParty/Win64/libxess.dll"
                   ],
    "Jogo2": ["config.exe", "arquivo1.dat"],
    "Jogo3": ["config.exe", "arquivo1.dat", "arquivo2.dat", "arquivo3.dat"],
}

class JogoWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(JogoWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.selected_game = None

        # Rótulo para escolher o jogo
        self.add_widget(Label(text='Escolha o jogo:', size_hint_y=None, height=40))

        # Layout para os jogos
        self.jogos_layout = GridLayout(cols=1, size_hint_y=None)
        self.jogos_layout.bind(minimum_height=self.jogos_layout.setter('height'))

        # Adicionando ToggleButtons para cada jogo
        self.jogo_buttons = {}
        for jogo in jogos_necessarios.keys():
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
                arquivos_faltando = self.verificar_arquivos(caminho_jogos, jogos_necessarios[jogo_selecionado])

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
