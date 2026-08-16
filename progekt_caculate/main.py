from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, CardTransition
from kivy.core.window import Window
from database import DatabaseManager
from screens import MainScreen, MaterialsScreen, CalculationScreen

# Встановлюємо комфортний початковий розмір вікна для тестування (опціонально)
Window.size = (450, 750)
Window.minimum_width = 360
Window.minimum_height = 600

class ProjectEstimatorApp(App):
    def build(self):
        self.title = "Калькулятор Кошторисів Проєктів"
        
        # Ініціалізація бази даних
        db_manager = DatabaseManager()
        
        # Використовуємо CardTransition для сучасних та плавних зміщень
        sm = ScreenManager(transition=CardTransition(direction='left', duration=0.3))
        
        # Реєстрація екранів
        sm.add_widget(MainScreen(db_manager=db_manager, name='main'))
        sm.add_widget(MaterialsScreen(name='materials'))
        sm.add_widget(CalculationScreen(db_manager=db_manager, name='calculation'))
        
        return sm

if __name__ == '__main__':
    ProjectEstimatorApp().run()
    