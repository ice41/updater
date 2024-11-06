
############################################################
# by ice41 if you use this code to anything keep the credits
############################################################
# plugins.py

import os
import sys
import importlib

def carregar_plugins(diretorio="plugins"):
    plugins = {}
    plugins_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), diretorio)

    if not os.path.exists(plugins_dir):
        print(f"Diretório '{plugins_dir}' não encontrado.")
        return plugins

    sys.path.append(plugins_dir)

    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            nome_modulo = filename[:-3]
            try:
                modulo = importlib.import_module(nome_modulo)
                importlib.reload(modulo)

                if hasattr(modulo, "executar"):
                    plugins[nome_modulo] = modulo.executar
            except ImportError as e:
                print(f"Erro ao carregar o plugin '{nome_modulo}': {e}")
    return plugins
