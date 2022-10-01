import re
import time
import zipfile

from bs4 import BeautifulSoup
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner
import requests

from utils import *

DOMAIN = 'https://www.missionjuno.swri.edu'


class PreviewContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super(PreviewContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.label = MDLabel(text='Please wait while the preview image is '
                             'begin downloaded...',
                             halign="center")
        # self.spinner = MDSpinner(active=True,
        #                          size=(dp(50), dp(50)),
        #                          size_hint=(None, None),
        #                          pos_hint={'center_x': 0.5})

        self.add_widget(self.label)
        # self.add_widget(self.spinner)

    def download_preview(self, res_url: str, res_id: int):
        webpage = requests.get(res_url)
        soup = BeautifulSoup(webpage.text, 'html.parser')

        lazy_img = soup.find('div', {'class': 'lazy_img'}).find('img')
        print(lazy_img)

        file_path = f'tmp/{res_id}_preview.jpg'
        download('file', file_path, requests.get(lazy_img['src']))
        self.label.text = ''
        self.add_widget(Image(source=file_path, size_hint_y=None))


class DownloadContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super(DownloadContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        # self.height = dp(100)
        self.label = MDLabel(text='Please wait while the resource is being '
                             'downloaded...\n'
                             'This may take a while. The app may become '
                             'unresponsive.',
                             halign="center")
        # self.spinner = MDSpinner(active=True,
        #                          size=(dp(50), dp(50)),
        #                          size_hint=(None, None),
        #                          pos_hint={'center_x': 0.5})
        self.add_widget(self.label)
        # self.add_widget(self.spinner)


class HomeScreen(MDScreen):
    pass


class DownloadScreen(MDScreen):

    def __init__(self, **kwargs):
        super(DownloadScreen, self).__init__(**kwargs)
        self.user_input = None
        self.res_id = None
        # print(self.ids.text_field)
        # self.ids.text_field.bind(
        #     on_text_validate=self.check_resource,
        #     on_focus=self.check_resource,
        # )
        # self.browser_layout = self.ids.browser_layout
        # self.add_widget(self.browser_layout)

    def check_resource(self):
        self.user_input = self.ids.text_field.text
        print(self.user_input)
        pattern = re.compile('https:\/\/www.missionjuno.swri.edu\/junocam\/'
                             'processing\?id=(\d+)')
        match = pattern.match(self.user_input)

        if match:
            self.res_id = match.group(1)
            self.ids.text_field.error = False
            self.ids.preview_resource_btn.disabled = False
            self.ids.download_resource_btn.disabled = False
        else:
            self.res_id = None
            self.ids.text_field.error = True
            self.ids.preview_resource_btn.disabled = True
            self.ids.download_resource_btn.disabled = True

    def show_preview_dialog(self):
        content = PreviewContent()
        ok_btn = MDFlatButton(text='OK')
        dialog = MDDialog(title='Preview',
                          type='custom',
                          content_cls=content,
                          buttons=[ok_btn],
                          on_open=self.preview_resource)
        ok_btn.bind(on_press=dialog.dismiss)
        dialog.open()
        # content.download_preview(self.user_input, self.res_id)

    def preview_resource(self, dialog):
        dialog.content_cls.download_preview(self.user_input, self.res_id)

    def show_download_dialog(self):
        content = DownloadContent()
        dialog = MDDialog(title=f'Downloading...',
                          type='custom',
                          content_cls=content,
                          on_open=self.download_resource,
                          on_pre_dismiss=self.show_done_snackbar)
        dialog.open()

    @staticmethod
    def show_done_snackbar(dialog):
        Snackbar(text='Done').open()

    def download_resource(self, dialog):
        r_page = requests.get(self.user_input)
        r_page_soup = BeautifulSoup(r_page.text, 'html.parser')
        # print(r_page_soup.title)
        processing = r_page_soup.find('div', {
            'class':
                'processing_tools half stack_full textright padT_half right'
        })

        save_dir = Path('data') / self.res_id
        for zip_tag in processing.find_all('a', {'class': 'marR download_zip'}):
            dl_url = DOMAIN + zip_tag['href']
            download('dir', save_dir, requests.get(dl_url, stream=True))

        for file in save_dir.iterdir():
            if file.suffix == '.zip':
                unzip(file)

        dialog.dismiss()


class MyFilesScreen(MDScreen):
    pass


class EditScreen(MDScreen):
    pass


class WutopiaApp(MDApp):

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

        self.data = get_path('./data')
        self.tmp = get_path('./tmp')

    # def on_stop(self):
    #     self.tmp.unlink()


if __name__ == '__main__':
    app = WutopiaApp()
    app.run()
