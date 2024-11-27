#news.py 1.2.3

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.logger import Logger
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
import requests
import os

NEWS_URL = "https://raw.githubusercontent.com/ice41/updater/refs/heads/main/news/news.json"
IMAGE_DIR = "temp_images"
NEWS_INTERVAL = 5  # Intervalo em segundos para trocar de notícia


def get_news():
    try:
        response = requests.get(NEWS_URL)
        if response.status_code == 200:
            return response.json()
        else:
            Logger.error(f"NewsWidget: Failed to fetch news, status code {response.status_code}")
            return []
    except Exception as e:
        Logger.error(f"NewsWidget: Error fetching news: {e}")
        return []


def download_image(url):
    """Downloads the image and returns the local path."""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    image_name = url.split("/")[-1]
    image_path = os.path.join(IMAGE_DIR, image_name)

    if not os.path.exists(image_path):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                Logger.info(f"NewsWidget: Image downloaded at {image_path}")
                return image_path
            else:
                Logger.error(f"NewsWidget: Failed to download image from {url}")
                return None
        except Exception as e:
            Logger.error(f"NewsWidget: Error downloading image {url} - {e}")
            return None
    return image_path


class NewsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Inicializa lista de notícias e índice
        self.news_items = get_news()
        self.current_index = 0

        # Layout de notícia única
        self.news_layout = BoxLayout(orientation="vertical", size_hint=(1, None), height=300, padding=20, spacing=10)
        self.add_widget(self.news_layout)

        # Exibe a primeira notícia e inicia o intervalo de troca
        self.display_news(self.current_index)
        Clock.schedule_interval(self.next_news, NEWS_INTERVAL)

    def display_news(self, index):
        """Exibe a notícia no índice especificado."""
        self.news_layout.clear_widgets()
        if not self.news_items:
            self.news_layout.add_widget(MDLabel(text="Nenhuma notícia disponível", halign="center"))
            return

        item = self.news_items[index]
        title = item.get("title", "Título não disponível")
        description = item.get("description", "Descrição não disponível")
        image_url = item.get("image_url", None)

        # Card para encapsular a notícia
        news_card = MDCard(
            orientation="vertical",
            padding=25,
            size_hint=(1, None),
            height=200,
            radius=[15, 15, 15, 15],
            elevation=8,
        )

        # Título
        news_card.add_widget(
            MDLabel(
                text=title,
                theme_text_color="Primary",
                font_style="H6",
                halign="center",
                size_hint_y=None,
                height=50,
            )
        )

        # Imagem
        if image_url:
            local_image_path = download_image(image_url)
            if local_image_path:
                news_card.add_widget(
                    FitImage(
                        source=local_image_path,
                        size_hint_y=None,
                        height=80,
                        radius=[15, 15, 0, 0],
                    )
                )
            else:
                news_card.add_widget(
                    MDLabel(text="Imagem indisponível", halign="center", size_hint_y=None, height=50)
                )

        # Descrição
        news_card.add_widget(
            MDLabel(
                text=description,
                theme_text_color="Secondary",
                font_style="Body1",
                halign="center",
                size_hint_y=None,
                height=100,
            )
        )

        # Botão para mais informações
        more_info_button = MDIconButton(
            icon="chevron-right",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: Logger.info(f"NewsWidget: Exibindo mais informações sobre {title}"),
        )
        news_card.add_widget(more_info_button)

        self.news_layout.add_widget(news_card)

    def next_news(self, dt):
        """Avança para a próxima notícia e exibe."""
        self.current_index = (self.current_index + 1) % len(self.news_items)
        self.display_news(self.current_index)


class NewsApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Tema azul
        self.theme_cls.theme_style = "Light"  # Tema claro
        return NewsWidget()


if __name__ == "__main__":
    NewsApp().run()
