from cefpython3 import cefpython as cef

from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget
from kivymd.app import MDApp
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
    def __init__(self, **kwargs):
        super(DownloadScreen, self).__init__(**kwargs)
        self.browser_layout = BrowserLayout()
        self.add_widget(self.browser_layout)

    def get_url(self):
        print(self.browser_layout.browser_widget._browser.GetUrl())

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
        self.manager.transition = NoTransition()

    def on_stop(self):
        self.manager.get_screen('download').destroy_browser()


if __name__ == '__main__':
    WutopiaApp().run()
    cef.Shutdown()
