# plugins.py

import os
import importlib
import sys
from kivy.uix.button import Button

# Lista dos plugins visíveis no menu
PLUGINS_VISIVEIS = ["jogos_cracked"]

def formatar_nome_plugin(nome_arquivo):
    """Converte o nome do arquivo em um título amigável para o menu."""
    return nome_arquivo.replace("_", " ").title()

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
                    # Usa o nome formatado ao adicionar ao dicionário de plugins
                    nome_amigavel = formatar_nome_plugin(nome_plugin)
                    print(f"Nome formatado do plugin: '{nome_amigavel}'")  # Adiciona o print para debug
                    plugins[nome_amigavel] = modulo.executar
                    print(f"Plugin '{nome_amigavel}' carregado para o menu.")
            except ImportError as e:
                print(f"Erro ao carregar o plugin '{nome_plugin}': {e}")

    return plugins

# Exemplo de como criar os botões no menu
def criar_botoes_menu(layout, plugins):
    """Cria botões para cada plugin no menu do layout especificado."""
    for nome_amigavel, funcao in plugins.items():
        button = Button(text=nome_amigavel, size_hint=(None, None), size=(120, 50))

        # Define a função para o botão com uma closure, evitando problemas com lambda
        def executar_plugin(instancia, func=funcao):
            func()

        button.bind(on_release=executar_plugin)
        layout.add_widget(button)
