import json
from pathlib import Path

from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen


class ResourceItem(MDCard, RoundedRectangularElevationBehavior):

    def __init__(self, preview_image: Path, title: str, subtitle: str):
        super(ResourceItem, self).__init__()
        self.resource_dir = preview_image.parent
        self.ids.image.source = str(preview_image)
        self.ids.title.text = title
        self.ids.subtitle.text = subtitle


class MyFilesScreen(MDScreen):

    def __init__(self, **kwargs):
        super(MyFilesScreen, self).__init__(**kwargs)
        self.resources = set()

    def on_enter(self, *args):
        for folder in Path('data').iterdir():
            if folder.name not in self.resources:
                self.resources.add(folder.name)
                with open(folder / 'DataSet' / f'{folder.name}-Metadata.json',
                          'r') as f:
                    metadata = json.load(f)
                self.ids.content.add_widget(
                    ResourceItem(folder / 'preview.jpg', metadata['TITLE'],
                                 metadata['PRODUCT_ID']))
