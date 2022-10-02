import json
from pathlib import Path

from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen


class ResourceItem(MDCard, RoundedRectangularElevationBehavior):

    def __init__(self, preview_image: Path, title: str, subtitle: str,
                 **kwargs):
        super(ResourceItem, self).__init__(**kwargs)
        self.resource_dir = preview_image.parent
        self.ids.image.source = str(preview_image)
        self.ids.title.text = title
        self.ids.subtitle.text = subtitle


class MyFilesScreen(MDScreen):

    def __init__(self, **kwargs):
        super(MyFilesScreen, self).__init__(**kwargs)
        self.resources = set()
        with open('metadata/id_to_metadata.json', 'r', encoding='utf-8') as f:
            self.fallback_metadata = json.load(f)

    def add_resource(self, folder: Path):
        metadata_json = folder / f'Dataset/{folder.name}-Metadata.json'
        if metadata_json.exists():  # Junocam images
            with open(metadata_json) as f:
                metadata = json.load(f)
            self.ids.content.add_widget(
                ResourceItem(folder / 'preview.jpg', metadata['TITLE'],
                             metadata['PRODUCT_ID']))
        else:  # Public images
            self.ids.content.add_widget(
                ResourceItem(folder / 'preview.jpg',
                             self.fallback_metadata[folder.name]['title'],
                             'This image is submitted by the public. '
                             'Unfortunately, image adjustments will be '
                             'unavailable.',
                             on_press=lambda x: x))

    def on_enter(self, *args):
        for folder in Path('data').iterdir():
            if folder.name not in self.resources:
                self.resources.add(folder.name)
                self.add_resource(folder)
