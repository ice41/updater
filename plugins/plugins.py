# plugins.py

import os
import importlib
import sys

# Defina os plugins que devem aparecer no menu
PLUGINS_VISIVEIS = ["jogos"]  # Lista de plugins visíveis no menu

# Nome do plugin de verificação automática
PLUGIN_VERIFICACAO_AUTOMATICA = "verificar_estrutura"

def carregar_plugins(diretorio="plugins"):
    """Carrega plugins, executando automaticamente o plugin de verificação e adicionando os outros ao menu."""
    plugins = {}
    sys.path.append(diretorio)

    for filename in os.listdir(diretorio):
        if filename.endswith(".py") and filename != "__init__.py":
            nome_plugin = filename[:-3]  # Nome do plugin sem a extensão .py
            try:
                modulo = importlib.import_module(nome_plugin)
                importlib.reload(modulo)

                # Executa automaticamente o plugin de verificação de estrutura
                if nome_plugin == PLUGIN_VERIFICACAO_AUTOMATICA and hasattr(modulo, "executar"):
                    print(f"Executando verificação automática: {nome_plugin}")
                    modulo.executar()
                
                # Adiciona outros plugins ao menu conforme PLUGINS_VISIVEIS
                elif nome_plugin in PLUGINS_VISIVEIS and hasattr(modulo, "executar"):
                    plugins[nome_plugin] = modulo.executar
                    print(f"Plugin '{nome_plugin}' carregado para o menu.")
            except ImportError as e:
                print(f"Erro ao carregar o plugin '{nome_plugin}': {e}")

    return plugins
