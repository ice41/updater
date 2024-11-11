# app_qt.py

import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, 
    QHBoxLayout, QGridLayout, QScrollArea, QDialog, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from utils import (get_current_version, get_server_version, download_update,
                   extract_update, move_files, remove_updater_folder, update_current_version)
from news import NewsWidget  # Assume que você converteu NewsWidget para PyQt
from plugins import carregar_plugins

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class UpdaterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Launcher NPED")
        self.setGeometry(100, 100, 950, 800)

        # Layout principal
        main_layout = QVBoxLayout()
        
        # Logo na parte superior
        logo_path = resource_path("nped.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path).scaled(150, 200, Qt.KeepAspectRatio)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(logo_label)

        # Layout para exibir versões
        version_layout = QHBoxLayout()
        self.current_version_label = QLabel(f"Versão do Launcher: {get_current_version()}")
        self.server_version_label = QLabel(f"Versão do Servidor: {get_server_version()}")
        version_layout.addWidget(self.current_version_label)
        version_layout.addWidget(self.server_version_label)

        main_layout.addLayout(version_layout)

        # Status da atualização e barra de progresso
        self.update_status_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        main_layout.addWidget(self.update_status_label)
        main_layout.addWidget(self.progress_bar)

        # Widget de notícias (Assumindo que o NewsWidget foi convertido para PyQt)
        self.news_widget = NewsWidget()
        main_layout.addWidget(self.news_widget)

        # Layout para botões na parte inferior
        button_layout = QHBoxLayout()

        # Botão de Menu para Plugins
        plugins_button = QPushButton("Menu")
        plugins_button.clicked.connect(self.show_plugins_popup)
        button_layout.addWidget(plugins_button)

        # Espaço para empurrar o botão "Atualizar" para o lado direito
        button_layout.addStretch(1)

        # Botão de Atualização
        self.update_button = QPushButton("Atualizar")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.on_update_button_press)
        button_layout.addWidget(self.update_button)

        main_layout.addLayout(button_layout)

        # Carregar plugins e verificar a versão do servidor
        self.plugins = carregar_plugins()
        self.check_version()

        self.setLayout(main_layout)

    def show_plugins_popup(self):
        popup = QDialog(self)
        popup.setWindowTitle("Plugins Disponíveis")
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        grid_layout = QGridLayout()
        plugin_widget = QWidget()
        plugin_widget.setLayout(grid_layout)
        
        for i, (nome_plugin, funcao_plugin) in enumerate(self.plugins.items()):
            btn = QPushButton(nome_plugin)
            btn.clicked.connect(lambda _, p=nome_plugin: self.executar_plugin(p))
            grid_layout.addWidget(btn, i // 3, i % 3)
        
        scroll_area.setWidget(plugin_widget)
        
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        popup.setLayout(layout)
        
        popup.setGeometry(300, 200, 400, 300)
        popup.exec_()

    def check_version(self):
        current_version = get_current_version()
        server_version = get_server_version()
        self.current_version_label.setText(f"Versão do Launcher: {current_version}")
        self.server_version_label.setText(f"Versão do Servidor: {server_version}")
        if current_version != server_version:
            self.update_button.setEnabled(True)

    def on_update_button_press(self):
        self.update_status_label.setText("Atualizando...")
        self.progress_bar.setValue(0)
        if download_update(self.update_progress):
            if extract_update():
                os.remove('atualizacao.zip')
                move_files(self.update_progress)
                remove_updater_folder()
                self.progress_bar.setValue(100)
                self.update_status_label.setText("Atualização concluída.")
                new_version = get_server_version()
                update_current_version(new_version)
            else:
                self.update_status_label.setText("Erro ao extrair a atualização.")
        else:
            self.update_status_label.setText("Erro ao baixar a atualização.")

    def update_progress(self, progress):
        """Atualiza o valor da barra de progresso."""
        self.progress_bar.setValue(progress)

    def executar_plugin(self, nome_plugin):
        if nome_plugin in self.plugins:
            self.plugins[nome_plugin]()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    updater_app = UpdaterApp()
    updater_app.show()
    sys.exit(app.exec_())
