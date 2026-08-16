from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_active = ""
        self.background_color = [0.95, 0.95, 0.97, 1]
        self.foreground_color = [0.1, 0.1, 0.1, 1]
        self.cursor_color = [0.15, 0.45, 0.9, 1]

        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.font_size = "16sp"
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(48)

        self.bind(focus=self._on_focus)

    def _on_focus(self, instance, focused):
        if not focused:
            return

        def scroll_to_input(_dt):
            app = App.get_running_app()

            if app and hasattr(app, "ensure_widget_visible"):
                app.ensure_widget_visible(self)

        Clock.schedule_once(scroll_to_input, 0.15)


class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = [0, 0, 0, 0]
        self.color = [1, 1, 1, 1]
        self.font_size = "16sp"
        self.bold = True
        self.size_hint_y = None
        self.height = dp(50)

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas,
            state=self.update_canvas,
            disabled=self.update_canvas
        )

    def update_canvas(self, *args):
        self.canvas.before.clear()

        with self.canvas.before:
            if self.disabled:
                Color(0.55, 0.55, 0.58, 1)
            elif self.state == "down":
                Color(0.08, 0.30, 0.70, 1)
            else:
                Color(0.15, 0.45, 0.90, 1)

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )


class FlatButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = [0, 0, 0, 0]
        self.color = [0.15, 0.45, 0.9, 1]
        self.font_size = "16sp"
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)


class DangerButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = [0, 0, 0, 0]
        self.color = [1, 1, 1, 1]
        self.font_size = "15sp"
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas,
            state=self.update_canvas
        )

    def update_canvas(self, *args):
        self.canvas.before.clear()

        with self.canvas.before:
            if self.state == "down":
                Color(0.65, 0.10, 0.10, 1)
            else:
                Color(0.82, 0.20, 0.20, 1)

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )


class ModernCheckbox(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)
    text = StringProperty("")

    def __init__(self, **kwargs):
        passed_text = kwargs.pop("text", "")
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.spacing = dp(12)
        self.padding = [dp(10), dp(4), dp(10), dp(4)]
        self.size_hint_y = None
        self.height = dp(54)

        self.box_indicator = Label(
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            pos_hint={"center_y": 0.5}
        )

        self.label_text = Label(
            text=passed_text,
            color=[0.1, 0.1, 0.1, 1],
            font_size="16sp",
            halign="left",
            valign="middle",
            pos_hint={"center_y": 0.5}
        )

        self.label_text.bind(
            size=self.label_text.setter("text_size")
        )

        self.add_widget(self.box_indicator)
        self.add_widget(self.label_text)

        self.text = passed_text

        self.bind(
            active=self.render_box,
            pos=self.render_box,
            size=self.render_box
        )

        self.render_box()

    def on_text(self, instance, value):
        if hasattr(self, "label_text"):
            self.label_text.text = value

    def render_box(self, *args):
        self.box_indicator.canvas.before.clear()

        with self.box_indicator.canvas.before:
            if self.active:
                Color(0.15, 0.45, 0.9, 1)

                RoundedRectangle(
                    pos=self.box_indicator.pos,
                    size=self.box_indicator.size,
                    radius=[dp(6)]
                )

                Color(1, 1, 1, 1)

                RoundedRectangle(
                    pos=(
                        self.box_indicator.x + dp(7),
                        self.box_indicator.y + dp(7)
                    ),
                    size=(dp(14), dp(14)),
                    radius=[dp(2)]
                )
            else:
                Color(0.68, 0.68, 0.70, 1)

                RoundedRectangle(
                    pos=self.box_indicator.pos,
                    size=self.box_indicator.size,
                    radius=[dp(6)]
                )

                Color(0.98, 0.98, 0.98, 1)

                RoundedRectangle(
                    pos=(
                        self.box_indicator.x + dp(3),
                        self.box_indicator.y + dp(3)
                    ),
                    size=(dp(22), dp(22)),
                    radius=[dp(4)]
                )

    def on_press(self):
        self.active = not self.active
