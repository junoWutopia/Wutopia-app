import json
from pathlib import Path

from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen


class ResourceItem(MDCard, RoundedRectangularElevationBehavior):

    def __init__(self, image: Path, title: str, subtitle: str):
        super(ResourceItem, self).__init__()
        self.ids.image.source = str(image)
        self.ids.title.text = title
        self.ids.subtitle.text = subtitle


class MyFilesScreen(MDScreen):

    def on_enter(self, *args):
        for folder in Path('data').iterdir():
            with open(folder / 'DataSet' / f'{folder.name}-Metadata.json', 'r')\
                    as f:
                metadata = json.load(f)
            self.ids.content.add_widget(
                ResourceItem(folder / 'preview.jpg', metadata['TITLE'],
                             metadata['PRODUCT_ID']))

    def on_leave(self, *args):
        self.ids.content.clear_widgets()
