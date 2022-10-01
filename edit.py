import shutil
from typing import Union

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField

from image_processing import *


class Adjustment(MDBoxLayout):

    def __init__(self,
                 name: str,
                 value: int = 0,
                 min: int = -100,
                 max: int = 100,
                 **kwargs):
        super(Adjustment, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(2)

        self.name = name
        self.value = value
        self.label = MDLabel(text=name)
        self.min = min
        self.max = max

        self.text_field = MDTextField(
            text=str(value),
            helper_text=f'Please enter a valid number between {min} and {max}',
            helper_text_mode='on_error',
            on_text_validate=self.update_value_from_text_field,
            size_hint_x=0.3)

        self.slider = MDSlider(value=value,
                               min=min,
                               max=max,
                               hint=True,
                               show_off=True)
        self.slider.bind(value=self.update_value_from_slider)

        self.add_widget(self.label)
        self.add_widget(MDBoxLayout(self.text_field, self.slider))

    def on_touch_up(self, touch):
        MDApp.get_running_app().edit_pipeline_callback()

    def update_value_from_slider(self, instance, value):
        self.value = self.slider.value
        self.text_field.text = f'{self.value:.0f}'

    def update_value_from_text_field(self, instance):
        try:
            value = float(self.text_field.text)
            if value < self.min or value > self.max:  # Out of range
                self.text_field.error = True
            else:
                self.value = value
                self.slider.value = self.value
                MDApp.get_running_app().edit_pipeline_callback()
        except ValueError:  # Error in conversion
            self.text_field.error = True


class EditScreen(MDScreen):

    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.img = None
        self.current_resource = None
        self.adjustments = {
            'brightness': Adjustment('Brightness', 0, -100, 100),
            'contrast': Adjustment('Contrast', 0, -100, 100),
            'hue': Adjustment('Hue', 0, -180, 180),
            'saturation': Adjustment('Saturation', 0, -100, 100),
            'lightness': Adjustment('Lightness', 0, -100, 100),
        }

        for adjustment in self.adjustments.values():
            self.ids.adjustments.add_widget(adjustment)

    def on_enter(self, *args):
        for adjustment in self.adjustments.values():
            adjustment.slider.value = 0
            adjustment.text_field.text = '0'

    def set_resource(self, resource_dir: Union[str, Path]):
        self.current_resource = resource_dir / 'ImageSet'
        RGBCombiner(self.current_resource)
        adjusted_path = self.current_resource / 'RGB_combined_adjusted.png'
        shutil.copy2(self.current_resource / 'RGB_combined.png', adjusted_path)
        self.img = Image.open(adjusted_path)
        self.ids.image.source = str(adjusted_path)

    @staticmethod
    def normalize(slider_value: float) -> float:
        if slider_value > 0:
            return 1.0 + slider_value / 100.0
        else:
            return 1.0 + slider_value / 200.0

    def pipeline(self):
        brightness_factor = self.normalize(self.adjustments['brightness'].value)
        contrast_factor = self.normalize(self.adjustments['contrast'].value)

        h = self.adjustments['hue'].value
        s = self.adjustments['saturation'].value
        l = self.adjustments['lightness'].value
        if s > 0:
            s *= 5
        if l > 0:
            l *= 3

        adjusted = adjust_brightness(self.img, brightness_factor)
        adjusted = adjust_contrast(adjusted, contrast_factor)
        adjusted = adjust_hsl(adjusted, h, s, l)

        adjusted.save(self.ids.image.source)
        self.ids.image.reload()
