from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard


class CardItem(MDCard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3


class AlternativeChooser(MDScreen):

    def __init__(self, **kwargs):
        super(AlternativeChooser, self).__init__(**kwargs)

    def on_start(self):
        for x in range[0, 21]:
            self.root.ids.ac_content.add_widget(CardItem())