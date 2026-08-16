from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import CardTransition, ScreenManager

from database import DatabaseManager
from screens import CalculationScreen, MainScreen, MaterialsScreen


class ProjectEstimatorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.navigation_history = []
        self.navigation_position = -1
        self.is_history_navigation = False

    def build(self):
        self.title = "Калькулятор кошторисів"

        Window.softinput_mode = "below_target"

        self.db_manager = DatabaseManager()

        self.screen_manager = ScreenManager(
            transition=CardTransition(
                direction="left",
                duration=0.22
            )
        )

        self.screen_manager.add_widget(
            MainScreen(
                db_manager=self.db_manager,
                name="main"
            )
        )

        self.screen_manager.add_widget(
            MaterialsScreen(
                db_manager=self.db_manager,
                name="materials"
            )
        )

        self.screen_manager.add_widget(
            CalculationScreen(
                db_manager=self.db_manager,
                name="calculation"
            )
        )

        self.navigation_history = ["main"]
        self.navigation_position = 0

        return self.screen_manager

    def on_start(self):
        Window.bind(on_keyboard=self.on_keyboard)

    def on_stop(self):
        Window.unbind(on_keyboard=self.on_keyboard)

    def navigate(self, screen_name):
        if self.screen_manager.current == screen_name:
            return

        if self.navigation_position < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[
                :self.navigation_position + 1
            ]

        self.navigation_history.append(screen_name)
        self.navigation_position += 1

        self.screen_manager.transition.direction = "left"
        self.screen_manager.current = screen_name

    def can_go_back(self):
        return self.navigation_position > 0

    def can_go_forward(self):
        return (
            self.navigation_position <
            len(self.navigation_history) - 1
        )

    def go_back(self):
        if not self.can_go_back():
            return False

        self.navigation_position -= 1

        target_screen = self.navigation_history[
            self.navigation_position
        ]

        self.screen_manager.transition.direction = "right"
        self.screen_manager.current = target_screen

        return True

    def go_forward(self):
        if not self.can_go_forward():
            return False

        self.navigation_position += 1

        target_screen = self.navigation_history[
            self.navigation_position
        ]

        self.screen_manager.transition.direction = "left"
        self.screen_manager.current = target_screen

        return True

    def on_keyboard(self, _window, key, _scancode, _codepoint, _modifiers):
        if key == 27:
            if self.go_back():
                return True

        return False

    def ensure_widget_visible(self, widget):
        screen = self.screen_manager.current_screen

        if hasattr(screen, "ensure_visible"):
            screen.ensure_visible(widget)


if __name__ == "__main__":
    ProjectEstimatorApp().run()
