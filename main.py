from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from download import DownloadScreen
from edit import EditScreen
from home import HomeScreen
from my_files import MyFilesScreen
from utils import *


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

        # self.data = get_path('./data')
        # self.tmp = get_path('./tmp')

    # def on_stop(self):
    #     self.tmp.unlink()

    def switch_screen(self, screen: str):
        self.manager.current = screen


if __name__ == '__main__':
    app = WutopiaApp()
    app.run()
