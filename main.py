import os
import shutil
import webbrowser

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from PIL import Image

import image_processing
import module_ddd
from module_ddd import Module3D
from download import DownloadScreen
from edit import EditScreen
from home import HomeScreen
from my_files import MyFilesScreen
from utils import *


class WutopiaApp(MDApp):

    def __init__(self, **kwargs):
        super(WutopiaApp, self).__init__()
        self.post_response = None
        self.text_field = None
        self.file_manager = MDFileManager(search='dirs',
                                          selector='folder',
                                          exit_manager=self.exit_manager,
                                          select_path=self.select_path)
        self.dialog = None
        self.save_path = None
        self.imgur_client = None

    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        get_path('data/')
        return Builder.load_file('main.kv')

    def on_start(self):
        self.manager: ScreenManager = self.root.ids.screen_manager
        self.manager.add_widget(HomeScreen(name='home'))
        self.manager.add_widget(DownloadScreen(name='download'))
        self.manager.add_widget(MyFilesScreen(name='my_files'))
        self.manager.add_widget(EditScreen(name='edit'))
        self.manager.add_widget(Module3D(name='module_ddd'))
        self.manager.transition = NoTransition()

        # self.data = get_path('./data')
        # self.tmp = get_path('./tmp')

    # def on_stop(self):
    #     self.tmp.unlink()

    @staticmethod
    def open_in_browser(url: str):
        webbrowser.open(url)

    def switch_screen(self, screen: str):
        self.manager.current = screen

    def select_resource(self, resource_dir: Path):
        self.manager.get_screen('edit').set_resource(resource_dir)
        self.switch_screen('edit')


    def select_resource_module(self, resource_dir: Path):
        module_ddd.Module3D.is_start_generate = True
        module_ddd.Module3D.generate_3d_dir = resource_dir


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

    def select_path(self, path: str):

        def cancel_btn_bind(*args):
            self.dialog.dismiss()
            self.exit_manager()

        def ok_btn_bind(*args):
            shutil.copy2(
                self.manager.get_screen('edit').current_resource /
                'RGB_combined_adjusted.png',
                self.save_path / self.text_field.text)
            Snackbar(text='Successfully saved to '
                     f'{self.save_path / self.text_field.text}').open()
            cancel_btn_bind()

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
        cancel_btn.bind(on_press=cancel_btn_bind)
        ok_btn.bind(on_press=ok_btn_bind)
        self.dialog.open()

    def exit_manager(self, *args):
        self.file_manager.close()

    def share_dialog(self):

        def cancel_btn_bind(*args):
            self.dialog.dismiss()

        def open_in_browser_bind(*args):
            webbrowser.open(f'https://imgur.com/{self.post_response["id"]}')

        def share_to_facebook_bind(*args):
            webbrowser.open('https://www.facebook.com/sharer/sharer.php?u='
                            f'{self.post_response["link"]}')

        def share_to_twitter_bind(*args):
            webbrowser.open('https://twitter.com/share?url='
                            f'{self.post_response["link"]}')

        def copy_to_clipboard_bind(*args):
            Clipboard.copy(self.post_response['link'])

        def ok_btn_bind(*args):
            if self.imgur_client is None:
                try:
                    self.imgur_client = ImgurClient('980a2d96e84f2fb', '')
                except ImgurClientError:
                    Snackbar(
                        text='Sorry, Imgur is currently unavailable.').open()
                    self.dialog.dismiss()
                    return

            if self.imgur_client is not None:
                self.post_response = self.imgur_client.upload_from_path(
                    self.manager.get_screen('edit').current_resource /
                    'RGB_combined_adjusted.png')
                print(self.post_response)

            cancel_btn_bind()
            self.dialog = MDDialog(
                title='Upload completed',
                type='custom',
                content_cls=MDStackLayout(
                    MDRectangleFlatIconButton(icon='web',
                                              text='Open in browser',
                                              on_release=open_in_browser_bind),
                    MDRectangleFlatIconButton(
                        icon='clipboard-outline',
                        text='Copy image direct link URL to clipboard',
                        on_release=copy_to_clipboard_bind),
                    MDRectangleFlatIconButton(
                        icon='facebook',
                        text='Share to Facebook',
                        on_release=share_to_facebook_bind,
                    ),
                    MDRectangleFlatIconButton(
                        icon='twitter',
                        text='Share to Twitter',
                        on_release=share_to_twitter_bind,
                    ),
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(120),
                ),
                buttons=[MDRaisedButton(text='OK', on_press=cancel_btn_bind)],
            )
            self.dialog.open()

        cancel_btn = MDFlatButton(
            text="No",
            theme_text_color="Custom",
        )
        ok_btn = MDRaisedButton(
            text="YES",
            theme_text_color="Custom",
        )
        self.dialog = MDDialog(
            title='Confirm upload to Imgur?',
            type='custom',
            buttons=[cancel_btn, ok_btn],
        )

        cancel_btn.bind(on_press=cancel_btn_bind)
        ok_btn.bind(on_press=ok_btn_bind)
        self.dialog.open()

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label,
                      tab_text):
        if tab_text == 'Filters':
            self.manager.get_screen('edit').ids.filters_tab.pipeline()


if __name__ == '__main__':
    app = WutopiaApp()
    app.run()
