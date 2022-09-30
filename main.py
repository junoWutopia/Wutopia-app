import re
import time

from bs4 import BeautifulSoup
from cefpython3 import cefpython as cef
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget
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
from kivymd.uix.spinner import MDSpinner

from cef_kivy.kivy_ import BrowserLayout
from cef_kivy.kivy_ import CefBrowser

from utils import *


class PreviewContent(MDBoxLayout):
    def __init__(self):
        super(PreviewContent, self).__init__()
        self.orientation = 'vertical'
        self.size_hint_y = None
        # self.label = MDLabel(text='Please wait while the preview image is '
        #                      'begin downloaded...',
        #                      halign="center",)
        # self.spinner = MDSpinner(active=True,
        #                          size=(dp(50), dp(50)),
        #                          size_hint=(None, None),
        #                          pos_hint={'center_x': 0.5})
        #
        # self.add_widget(self.label)
        # self.add_widget(self.spinner)

    def download_preview(self, res_url: str):
        webpage = requests.get(res_url)
        soup = BeautifulSoup(webpage.text, 'html.parser')

        lazy_img = soup.find('div', {'class': 'lazy_img'}).find('img')
        print(lazy_img)

        tmp = get_path('./tmp')
        download(tmp / 'preview.png', requests.get(lazy_img['src']))

        self.add_widget(Image(source='tmp/preview.png', size_hint_y=None))


class HomeScreen(MDScreen):
    pass


class DownloadScreen(MDScreen):

    # download_enabled = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(DownloadScreen, self).__init__(**kwargs)
        self.user_input = None
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
                             'processing\?id=\d+')

        if pattern.match(self.user_input):
            self.ids.text_field.error = False
            self.ids.preview_resource_btn.disabled = False
            self.ids.download_resource_btn.disabled = False
        else:
            self.ids.text_field.error = True
            self.ids.preview_resource_btn.disabled = True
            self.ids.download_resource_btn.disabled = True

    def preview_resource(self):
        content = PreviewContent()
        ok_btn = MDFlatButton(text='OK')
        dialog = MDDialog(
            title='Preview',
            type='custom',
            content_cls=content,
            buttons=[ok_btn]
        )
        ok_btn.bind(on_press=dialog.dismiss)
        dialog.open()
        content.download_preview(self.user_input)

    def download_resource(self):
        pass

    def destroy_browser(self):
        # This is required for a clean shutdown of CEF.
        self.browser_layout.browser_widget._browser.CloseBrowser(True)
        del self.browser_layout.browser_widget._browser


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
        self.manager.add_widget(EditScreen(name='edit'))
        self.manager.transition = NoTransition()

    # def on_stop(self):
    # self.manager.get_screen('download').destroy_browser()
    #     self.browser_layout.browser_widget._browser.CloseBrowser(True)
    #     del self.browser_layout.browser_widget._browser


if __name__ == '__main__':
    app = WutopiaApp()
    app.run()
    cef.Shutdown()
