from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, BooleanProperty

class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = [0.95, 0.95, 0.97, 1]
        self.foreground_color = [0.1, 0.1, 0.1, 1]
        self.cursor_color = [0.2, 0.4, 0.8, 1]
        # Зменшено відступи, щоб поле було акуратнішим
        self.padding = [12, 8, 12, 8]
        self.font_size = '15sp'
        self.multiline = False
        self.size_hint_y = None
        self.height = 40  # Оптимальна висота замість 50

class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        self.color = [1, 1, 1, 1]
        self.font_size = '15sp'
        self.bold = True
        self.size_hint_y = None
        self.height = 42  # Робимо кнопку трохи нижчою та охайнішою
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == 'normal':
                Color(0.15, 0.45, 0.9, 1)
            else:
                Color(0.1, 0.35, 0.75, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])

class FlatButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        self.color = [0.15, 0.45, 0.9, 1]
        self.font_size = '15sp'
        self.bold = True
        self.size_hint_y = None
        self.height = 42

class ModernCheckbox(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)
    text = StringProperty("")

    def __init__(self, **kwargs):
        passed_text = kwargs.pop('text', "")
        super().__init__(**kwargs)
        
        self.orientation = 'horizontal'
        self.spacing = 10
        self.size_hint_y = None
        self.height = 40

        self.box_indicator = Label(size_hint=(None, None), size=(22, 22), pos_hint={'center_y': 0.5})
        self.label_text = Label(text=passed_text, color=[0.1, 0.1, 0.1, 1], font_size='15sp', halign='left', valign='middle', pos_hint={'center_y': 0.5})
        self.label_text.bind(size=self.label_text.setter('text_size'))

        self.add_widget(self.box_indicator)
        self.add_widget(self.label_text)
        
        self.text = passed_text
        
        self.bind(active=self.render_box, pos=self.render_box, size=self.render_box)
        self.render_box()

    def on_text(self, instance, value):
        if hasattr(self, 'label_text'):
            self.label_text.text = value

    def render_box(self, *args):
        self.box_indicator.canvas.before.clear()
        with self.box_indicator.canvas.before:
            if self.active:
                Color(0.15, 0.45, 0.9, 1)
                RoundedRectangle(pos=self.box_indicator.pos, size=self.box_indicator.size, radius=[5])
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=(self.box_indicator.pos[0]+6, self.box_indicator.pos[1]+6), size=(10, 10), radius=[1.5])
            else:
                Color(0.7, 0.7, 0.7, 1)
                RoundedRectangle(pos=self.box_indicator.pos, size=self.box_indicator.size, radius=[5])
                Color(0.98, 0.98, 0.98, 1)
                RoundedRectangle(pos=(self.box_indicator.pos[0]+2, self.box_indicator.pos[1]+2), size=(18, 18), radius=[3])

    def on_press(self):
        self.active = not self.active