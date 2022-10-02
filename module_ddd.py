import json
from pathlib import Path


from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard

from image_processing import Magnetic_field


class Module3DItem(MDCard, RoundedRectangularElevationBehavior):

    def __init__(self, preview_image: Path, title: str, subtitle: str, **kwargs):
        super(Module3DItem, self).__init__(**kwargs)
        self.resource_dir = preview_image.parent
        self.ids.module_image.source = str(preview_image)
        self.ids.module_title.text = title
        self.ids.module_subtitle.text = subtitle


class Module3D(MDScreen):
    def __init__(self, **kwargs):
        super(Module3D, self).__init__(**kwargs)
        self.resources = set()
        with open('metadata/id_to_metadata.json', 'r', encoding='utf-8') as f:
            self.fallback_metadata = json.load(f)
        self.dir=''
        self.is_dir_set = False

    def add_resource(self, folder: Path):
        metadata_json = folder / f'Dataset/{folder.name}-Metadata.json'
        if metadata_json.exists():  # Junocam images
            with open(metadata_json) as f:
                metadata = json.load(f)
            self.ids.module_content.add_widget(
                Module3DItem(folder / 'preview.jpg', metadata['TITLE'],
                             metadata['PRODUCT_ID']))
        else:  # Public images
            self.ids.module_content.add_widget(
                Module3DItem(folder / 'preview.jpg',
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

    is_start_generate = False
    generate_3d_dir = ''

    def start_generate(self):
        if self.is_start_generate:
            Magnetic_field(self.generate_3d_dir, self.ids.external_shell.value, int(self.ids.layers.value))