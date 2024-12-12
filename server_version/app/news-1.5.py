#news.py 1.6

import requests
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

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
        self.orientation = 'vertical'

        # Inicializa lista de notícias e índice
        self.news_items = get_news()
        self.current_index = 0

        # Layout de notícia única
        self.news_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(500), spacing=dp(10), padding=dp(10))
        self.add_widget(self.create_card(self.news_layout))

        # Exibe a primeira notícia e inicia o intervalo de troca
        self.display_news(self.current_index)
        Clock.schedule_interval(self.next_news, NEWS_INTERVAL)

    def create_card(self, content):
        """Envolve o conteúdo em um card com bordas e fundo estilizado."""
        card = BoxLayout(size_hint=(1, None), height=dp(400), padding=dp(10))
        with card.canvas.before:
            Color(1, 1, 1, 1)  # Fundo branco
            self.bg_rect = Rectangle(size=card.size, pos=card.pos)
            Color(0, 0, 0, 0.1)  # Sombra leve
            Rectangle(size=(card.size[0] + dp(10), card.size[1] + dp(10)), pos=(card.pos[0] - dp(5), card.pos[1] - dp(5)))
        card.bind(size=self.update_rect, pos=self.update_rect)
        card.add_widget(content)
        return card

    def update_rect(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def display_news(self, index):
        """Exibe a notícia no índice especificado."""
        self.news_layout.clear_widgets()
        if not self.news_items:
            self.news_layout.add_widget(Label(text="Nenhuma notícia disponível", size_hint_y=None, height=dp(40)))
            return

        item = self.news_items[index]
        title = item.get('title', 'Título não disponível')
        description = item.get('description', 'Descrição não disponível')
        image_url = item.get('image_url', None)

        # Título estilizado
        title_label = Label(
            text=title,
            color=(0.1, 0.5, 0.8, 1),  # Azul suave
            bold=True,
            font_size='20sp',
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.news_layout.add_widget(title_label)

        # Espaço entre título e imagem
        self.news_layout.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))

        # Imagem da notícia
        if image_url:
            local_image_path = download_image(image_url)
            if local_image_path:
                image = KivyImage(source=local_image_path, size_hint=(1, None), height=dp(300))
                self.news_layout.add_widget(image)
            else:
                self.news_layout.add_widget(Label(text="Imagem indisponível", size_hint_y=None, height=dp(40)))

        # Espaço entre imagem e descrição
        self.news_layout.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))

        # Descrição estilizada
        description_label = Label(
            text=description,
            font_size='16sp',
            size_hint_y=None,
            height=dp(80),
            halign='center',
            valign='middle',
            color=(0, 0, 0, 0.8)  # Preto com opacidade
        )
        description_label.bind(size=description_label.setter('text_size'))
        self.news_layout.add_widget(description_label)

    def next_news(self, dt):
        """Avança para a próxima notícia e exibe."""
        self.current_index = (self.current_index + 1) % len(self.news_items)
        self.display_news(self.current_index)
