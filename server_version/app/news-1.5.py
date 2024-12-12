#news.py 1.5.1

import requests
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.anchorlayout import AnchorLayout

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
        self.news_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=400)
        self.add_widget(self.news_layout)

        # Exibe a primeira notícia e inicia o intervalo de troca
        self.display_news(self.current_index)
        Clock.schedule_interval(self.next_news, NEWS_INTERVAL)

    def display_news(self, index):
        """Exibe a notícia no índice especificado."""
        self.news_layout.clear_widgets()
        if not self.news_items:
            self.news_layout.add_widget(Label(text="Nenhuma notícia disponível", size_hint_y=None, height=40))
            return

        item = self.news_items[index]
        title = item.get('title', 'Título não disponível')
        description = item.get('description', 'Descrição não disponível')
        image_url = item.get('image_url', None)

        # Título em negrito e azul claro, centralizado
        title_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=45)
        title_label = Label(text=title, color=(0.5, 0.8, 1, 1), bold=True)  # Azul claro
        title_layout.add_widget(title_label)
        self.news_layout.add_widget(title_layout)

        # Descrição centralizada
        description_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=60)
        description_label = Label(text=description)
        description_layout.add_widget(description_label)
        self.news_layout.add_widget(description_layout)

        # Imagem da notícia centralizada
        if image_url:
            local_image_path = download_image(image_url)
            if local_image_path:
                image_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=50)
                image = KivyImage(source=local_image_path, size_hint=(None, None), width=600, height=60)
                image_layout.add_widget(image)
                self.news_layout.add_widget(image_layout)
            else:
                no_image_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=20)
                no_image_label = Label(text="Imagem indisponível")
                no_image_layout.add_widget(no_image_label)
                self.news_layout.add_widget(no_image_layout)

    def next_news(self, dt):
        """Avança para a próxima notícia e exibe."""
        self.current_index = (self.current_index + 1) % len(self.news_items)
        self.display_news(self.current_index)

