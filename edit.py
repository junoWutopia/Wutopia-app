import shutil
from typing import Union

from kivymd.uix.screen import MDScreen

from image_processing import *


class EditScreen(MDScreen):

    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.img = None
        self.current_resource = None

    def on_enter(self, *args):
        self.ids.brightness_slider.value = 0
        self.ids.contrast_slider.value = 0

    def set_resource(self, resource_dir: Union[str, Path]):
        self.current_resource = resource_dir / 'ImageSet'
        RGBCombiner(self.current_resource)
        adjusted_path = self.current_resource / 'RGB_combined_adjusted.png'
        shutil.copy2(self.current_resource / 'RGB_combined.png', adjusted_path)
        self.img = Image.open(adjusted_path)
        self.ids.image.source = str(adjusted_path)

    @staticmethod
    def normalize(slider_value: int) -> float:
        if slider_value > 0:
            return 1.0 + slider_value / 100.0
        else:
            return 1.0 + slider_value / 200.0

    def pipeline(self):
        brightness_factor = self.normalize(self.ids.brightness_slider.value)
        contrast_factor = self.normalize(self.ids.contrast_slider.value)

        adjusted = adjust_brightness(self.img, brightness_factor)
        adjusted = adjust_contrast(adjusted, contrast_factor)

        adjusted.save(self.ids.image.source)

        self.ids.image.reload()
