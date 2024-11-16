# plugins.py

import os
import importlib
import sys
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

# Lista dos plugins visíveis no menu
PLUGINS_VISIVEIS = ["jogos_cracked"]

def formatar_nome_plugin(nome_arquivo):
    """Converte o nome do arquivo em um título amigável para o menu."""
    # Remove underscores, substitui por espaços e converte para um formato amigável
    return nome_arquivo.replace("_", " ").replace(".py", "").title()

def carregar_plugins(diretorio="plugins"):
    """Carrega os plugins e retorna apenas os que devem aparecer no menu."""
    plugins = {}
    sys.path.append(diretorio)

    for filename in os.listdir(diretorio):
        if filename.endswith(".py") and filename != "__init__.py":
            nome_plugin = filename[:-3]  # Remove a extensão .py
            try:
                modulo = importlib.import_module(nome_plugin)
                importlib.reload(modulo)

                # Adiciona ao menu se o plugin estiver na lista de visíveis e tiver uma função executar
                if nome_plugin in PLUGINS_VISIVEIS and hasattr(modulo, "executar"):
                    nome_amigavel = formatar_nome_plugin(nome_plugin)  # Aplica a formatação amigável
                    print(f"Plugin '{nome_amigavel}' carregado para o menu.")  # Exibe o nome formatado no terminal
                    plugins[nome_amigavel] = modulo.executar
            except ImportError as e:
                print(f"Erro ao carregar o plugin '{nome_plugin}': {e}")

    return plugins

def criar_botoes_menu(layout, plugins):
    """Cria botões para cada plugin no menu, organizados verticalmente em um GridLayout."""
    # Usa um GridLayout com 1 coluna para dispor os botões verticalmente
    botoes_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
    botoes_layout.bind(minimum_height=botoes_layout.setter('height'))  # Ajusta a altura conforme o conteúdo

    for nome_amigavel, funcao in plugins.items():
        button = Button(text=nome_amigavel, size_hint_y=None, height=50)

        # Define a função para o botão com uma closure, evitando problemas com lambda
        def executar_plugin(instancia, func=funcao):
            func()

        button.bind(on_release=executar_plugin)
        botoes_layout.add_widget(button)

    # Adiciona o layout de botões ao layout principal
    layout.add_widget(botoes_layout)
