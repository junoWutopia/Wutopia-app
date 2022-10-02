import json

from bs4 import BeautifulSoup
from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner
import requests

from utils import *

DOMAIN = 'https://www.missionjuno.swri.edu'
RESOURCE_URL_PREFIX = f'{DOMAIN}/junocam/processing?id='


class PreviewDialogContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super(PreviewDialogContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.label = MDLabel(text='Please wait while the preview image is '
                             'being downloaded...',
                             halign="center")
        # self.spinner = MDSpinner(active=True,
        #                          size=(dp(50), dp(50)),
        #                          size_hint=(None, None),
        #                          pos_hint={'center_x': 0.5})

        self.add_widget(self.label)
        # self.add_widget(self.spinner)

    def download_preview(self, resource_id: int):
        webpage = requests.get(f'{RESOURCE_URL_PREFIX}{resource_id}')
        soup = BeautifulSoup(webpage.text, 'html.parser')

        lazy_img = soup.find('div', {'class': 'lazy_img'}).find('img')

        file_path = f'data/{resource_id}/preview.jpg'
        download('file', file_path, requests.get(lazy_img['src']))
        self.label.text = ''
        self.add_widget(Image(source=file_path, size_hint_y=None))


class DownloadDialogContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super(DownloadDialogContent, self).__init__(**kwargs)
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


class DownloadScreen(MDScreen):

    def __init__(self, **kwargs):
        super(DownloadScreen, self).__init__(**kwargs)
        self.resource_id = None
        self.resource_title = None

        with open('metadata/id_to_metadata.json', 'r', encoding='utf-8') as f:
            self.id_to_metadata = json.load(f)

        with open('metadata/title_to_id.json', 'r', encoding='utf-8') as f:
            self.title_to_id = json.load(f)
        # Maintain case-insensitivity
        upper_keys = dict()
        for k, v in self.title_to_id.items():
            upper_keys[k.upper()] = v
        self.title_to_id = upper_keys

        with open('metadata/product_id_to_id.json', 'r', encoding='utf-8') as f:
            self.product_id_to_id = json.load(f)

    def update_status(self, valid: bool, error_message: str = 'Invalid input'):
        if valid:
            self.resource_title = self.id_to_metadata[str(
                self.resource_id)]['title']
            self.ids.text_field.error = False
            self.ids.preview_resource_btn.disabled = False
            self.ids.download_resource_btn.disabled = False
        else:
            self.ids.text_field.helper_text = error_message
            self.ids.text_field.error = True
            self.ids.preview_resource_btn.disabled = True
            self.ids.download_resource_btn.disabled = True

    def check_resource(self):
        user_input = self.ids.text_field.text
        url_pattern = re.compile('^https://www.missionjuno.swri.edu/junocam/'
                                 'processing\?id=(\d+)$')
        url_match = url_pattern.match(user_input)

        if url_match:
            self.resource_id = url_match.group(1)
            self.update_status(True)
        elif user_input in self.title_to_id.keys():
            resource_ids = self.title_to_id[user_input.upper()]
            if len(resource_ids) > 1:
                self.update_status(
                    False,
                    f'Title ambiguity detected: Images IDs {resource_ids} have '
                    'the same title.')
            else:
                self.resource_id = resource_ids[0]
                self.update_status(True)
        elif user_input in self.product_id_to_id.keys():
            self.resource_id = self.product_id_to_id[user_input]
            self.update_status(True)
        else:
            self.update_status(False)

    def show_preview_dialog(self):
        content = PreviewDialogContent()
        ok_btn = MDFlatButton(text='OK')
        dialog = MDDialog(title=f'Previewing {self.resource_title}',
                          type='custom',
                          content_cls=content,
                          buttons=[ok_btn],
                          on_open=self.preview_resource)
        ok_btn.bind(on_press=dialog.dismiss)
        dialog.open()
        # content.download_preview(self.user_input, self.res_id)

    def preview_resource(self, dialog):
        dialog.content_cls.download_preview(self.resource_id)

    def show_download_dialog(self):
        content = DownloadDialogContent()
        dialog = MDDialog(title=f'Downloading {self.resource_title}',
                          type='custom',
                          content_cls=content,
                          on_open=self.download_resource,
                          on_pre_dismiss=self.show_done_snackbar)
        dialog.open()

    @staticmethod
    def show_done_snackbar(dialog):
        Snackbar(text='Done').open()

    def download_resource(self, dialog):
        r_page = requests.get(f'{RESOURCE_URL_PREFIX}{self.resource_id}')
        r_page_soup = BeautifulSoup(r_page.text, 'html.parser')
        # print(r_page_soup.title)
        processing = r_page_soup.find('div', {
            'class':
                'processing_tools half stack_full textright padT_half right'
        })

        save_dir = Path('data') / str(self.resource_id)

        if not (save_dir / 'preview.jpg').exists():
            PreviewDialogContent().download_preview(self.resource_id)

        for zip_tag in processing.find_all('a', {'class': 'marR download_zip'}):
            dl_url = DOMAIN + zip_tag['href']
            download('dir', save_dir, requests.get(dl_url, stream=True))

        for file in save_dir.iterdir():
            if file.suffix == '.zip':
                unzip(file)

        dialog.dismiss()
