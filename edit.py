import shutil
from typing import Union

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.slider import MDSlider
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.tab import MDTabsBase
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
            # on_text_validate=self.update_value_from_text_field,
            size_hint_x=0.3)
        self.text_field.bind(text=self.update_value_from_text_field)

        self.slider = MDSlider(value=value,
                               min=min,
                               max=max,
                               hint=True,
                               show_off=False)

        self.add_widget(self.label)
        self.add_widget(MDBoxLayout(self.text_field, self.slider))

    def on_touch_up(self, touch):
        self.value = self.slider.value
        self.text_field.text = f'{self.value:.0f}'
        MDApp.get_running_app().basic_adjustments_pipeline_callback()

    def update_value_from_text_field(self, *args):
        try:
            value = float(self.text_field.text)
            if value < self.min or value > self.max:  # Out of range
                self.text_field.error = True
            else:
                self.value = value
                self.slider.value = self.value
                MDApp.get_running_app().basic_adjustments_pipeline_callback()
        except ValueError:  # Error in conversion
            self.text_field.error = True


class BasicAdjustmentsTab(MDFloatLayout, MDTabsBase):

    def __init__(self, **kwargs):
        super(BasicAdjustmentsTab, self).__init__(**kwargs)

        self.adjustments = {
            'brightness': Adjustment('Brightness', 0, -100, 100),
            'contrast': Adjustment('Contrast', 0, -100, 100),
            'hue': Adjustment('Hue', 0, -180, 180),
            'saturation': Adjustment('Saturation', 0, -100, 100),
            'lightness': Adjustment('Lightness', 0, -100, 100),
        }

        self.initialized = False
        self.last_adjustment = (None, None, None, None, None)

    def on_enter(self):
        if not self.initialized:
            for adjustment in self.adjustments.values():
                self.ids.adjustments_box.add_widget(adjustment)
            self.initialized = True

        for adjustment in self.adjustments.values():
            adjustment.slider.value = 0
            adjustment.text_field.text = '0'

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

        this_adjustment = (brightness_factor, contrast_factor, h, s, l)
        if this_adjustment == self.last_adjustment:
            return
        self.last_adjustment = this_adjustment

        adjusted = Image.open(
            MDApp.get_running_app().manager.get_screen('edit').ids.image.source)
        adjusted = adjust_brightness(adjusted, brightness_factor)
        adjusted = adjust_contrast(adjusted, contrast_factor)
        adjusted = adjust_hsl(adjusted, h, s, l)

        MDApp.get_running_app().save_image_callback(adjusted)


class FilterTile(MDSmartTile):

    def __init__(self, filter_name: str, preview_image: Path, **kwargs):
        super(FilterTile, self).__init__(**kwargs)
        self.ids.label.text = filter_name
        self.source = str(preview_image)

    def on_press(self, *args):
        MDApp.get_running_app().save_image_callback(Image.open(self.source))


class FiltersTab(MDScrollView, MDTabsBase):

    def __init__(self, **kwargs):
        super(FiltersTab, self).__init__(**kwargs)
        self.initialized = False

    def on_enter(self):
        edit_screen = MDApp.get_running_app().manager.get_screen('edit')
        colormapped_dir = Path(
            edit_screen.ids.image.source).parent / 'colormapped'

        colormapper = Colormapper(edit_screen.rgb_combined, colormapped_dir)
        colormapper.generate()

        self.ids.grid.add_widget(
            FilterTile('None', colormapped_dir.parent / 'RGB_combined.png'))
        for file in colormapped_dir.iterdir():
            self.ids.grid.add_widget(FilterTile(file.stem, file))


class EditScreen(MDScreen):

    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.rgb_combined = None
        self.current_resource = None

    def on_enter(self, *args):
        self.ids.basic_adjustments_tab.on_enter()
        self.ids.filters_tab.on_enter()

    def set_resource(self, resource_dir: Union[str, Path]):
        self.current_resource = resource_dir / 'ImageSet'
        RGBCombiner(self.current_resource)
        adjusted_path = self.current_resource / 'RGB_combined_adjusted.png'
        shutil.copy2(self.current_resource / 'RGB_combined.png', adjusted_path)
        self.rgb_combined = Image.open(adjusted_path)
        self.ids.image.source = str(adjusted_path)
