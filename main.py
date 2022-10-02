import os
import shutil

from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from PIL import Image

from download import DownloadScreen
from edit import EditScreen
from home import HomeScreen
from my_files import MyFilesScreen
from utils import *


class WutopiaApp(MDApp):

    def __init__(self, **kwargs):
        super(WutopiaApp, self).__init__()
        self.text_field = None
        self.file_manager = MDFileManager(search='dirs',
                                          selector='folder',
                                          exit_manager=self.exit_manager,
                                          select_path=self.select_path)
        self.dialog = None
        self.save_path = None

    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        return Builder.load_file('main.kv')

    def on_start(self):
        self.manager: ScreenManager = self.root.ids.screen_manager
        self.manager.add_widget(HomeScreen(name='home'))
        self.manager.add_widget(DownloadScreen(name='download'))
        self.manager.add_widget(MyFilesScreen(name='my_files'))
        self.manager.add_widget(EditScreen(name='edit'))
        self.manager.transition = NoTransition()

        # self.data = get_path('./data')
        # self.tmp = get_path('./tmp')

    # def on_stop(self):
    #     self.tmp.unlink()

    def switch_screen(self, screen: str):
        self.manager.current = screen

    def select_resource(self, resource_dir: Path):
        self.manager.get_screen('edit').set_resource(resource_dir)
        self.switch_screen('edit')

    def basic_adjustments_pipeline_callback(self):
        self.manager.get_screen('edit').ids.basic_adjustments_tab.pipeline()

    def save_image_callback(self, img: Image):
        edit_screen = self.manager.get_screen('edit')
        img.save(edit_screen.ids.image.source)
        edit_screen.ids.image.reload()

    def save_dialog(self):
        self.file_manager_open()

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser('~'))

    def cancel_btn_bind(self, *args):
        self.dialog.dismiss()
        self.exit_manager()

    def ok_btn_bind(self, *args):
        shutil.copy2(
            self.manager.get_screen('edit').current_resource /
            'RGB_combined_adjusted.png', self.save_path / self.text_field.text)
        Snackbar(text='Successfully saved to '
                 f'{self.save_path / self.text_field.text}').open()
        self.cancel_btn_bind()

    def select_path(self, path: str):
        self.save_path = Path(path)
        cancel_btn = MDFlatButton(
            text="CANCEL",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
        )
        ok_btn = MDFlatButton(
            text="OK",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
        )
        self.text_field = MDTextField(
            hint_text='File name (please end with the .png extension)',
            helper_text='Example: my_awesome_image.png')
        self.dialog = MDDialog(
            title='Save image',
            type='custom',
            content_cls=self.text_field,
            buttons=[cancel_btn, ok_btn],
        )
        cancel_btn.bind(on_press=self.cancel_btn_bind)
        ok_btn.bind(on_press=self.ok_btn_bind)
        self.dialog.open()

    def exit_manager(self, *args):
        self.file_manager.close()


if __name__ == '__main__':
    app = WutopiaApp()
    app.run()
