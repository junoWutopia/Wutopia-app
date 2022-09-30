import re

from cefpython3 import cefpython as cef
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from cef_kivy.kivy_ import BrowserLayout
from cef_kivy.kivy_ import CefBrowser


class HomeScreen(MDScreen):
    pass


class DownloadScreen(MDScreen):

    # download_enabled = BooleanProperty(False)

    # def __init__(self, **kwargs):
        # super(DownloadScreen, self).__init__(**kwargs)
        # self.browser_layout = self.ids.browser_layout
        # self.add_widget(self.browser_layout)

    def destroy_browser(self):
        # This is required for a clean shutdown of CEF.
        self.browser_layout.browser_widget._browser.CloseBrowser(True)
        del self.browser_layout.browser_widget._browser


class EditScreen(MDScreen):
    pass


class WutopiaApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        return Builder.load_file('wutopia.kv')

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
