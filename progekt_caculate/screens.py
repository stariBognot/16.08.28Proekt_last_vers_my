import os
import shutil
import time
from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from widgets import ModernTextInput, ModernButton, ModernCheckbox, FlatButton
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db = db_manager
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        self.search_input = ModernTextInput(hint_text="Пошук проєктів...")
        self.search_input.bind(text=self.on_search_change)
        main_layout.add_widget(self.search_input)
        self.scroll = ScrollView(do_scroll_x=False)
        self.projects_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.projects_list.bind(minimum_height=self.projects_list.setter('height'))
        self.scroll.add_widget(self.projects_list)
        main_layout.add_widget(self.scroll)
        btn_add = ModernButton(text="+ Додати проєкт")
        btn_add.bind(on_release=self.show_create_popup)
        main_layout.add_widget(btn_add)
        self.add_widget(main_layout)
        self.all_projects = []

    def on_enter(self):
        self.refresh_projects()

    def refresh_projects(self):
        self.all_projects = self.db.get_all_projects()
        self.filter_projects(self.search_input.text)

    def on_search_change(self, instance, value):
        self.filter_projects(value)

    def filter_projects(self, query):
        self.projects_list.clear_widgets()
        for p in self.all_projects:
            if query.lower() in p["name"].lower():
                btn = Button(text=f"  {p['name']}  |  Сума: {p['total_sum']:.3f}", size_hint_y=None, height=55, background_normal='', background_color=[1, 1, 1, 1], color=[0.1, 0.1, 0.1, 1], font_size='15sp', halign='left', valign='middle')
                btn.bind(size=btn.setter('text_size'))
                with btn.canvas.before:
                    Color(0.9, 0.9, 0.92, 1)
                    RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                btn.bind(pos=self._update_item_bg, size=self._update_item_bg)
                btn.bind(on_release=lambda instance, pid=p["id"]: self.open_project(pid))
                self.projects_list.add_widget(btn)

    def _update_item_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.9, 0.9, 0.92, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[8])

    def show_create_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=12, padding=10)
        lbl = Label(text="Введіть назву проєкту:", color=[0.1, 0.1, 0.1, 1], font_size='15sp')
        txt_name = ModernTextInput(hint_text="Назва проєкту")
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        btn_cancel = FlatButton(text="Скасувати"); btn_ok = ModernButton(text="Створити")
        btn_layout.add_widget(btn_cancel); btn_layout.add_widget(btn_ok)
        content.add_widget(lbl); content.add_widget(txt_name); content.add_widget(btn_layout)
        popup = Popup(title="Новий проєкт", content=content, size_hint=(0.85, None), height=200, background_color=[1, 1, 1, 1])
        popup.title_color = [0.1, 0.1, 0.1, 1]
        btn_cancel.bind(on_release=popup.dismiss)
        def confirm_create(inst):
            name = txt_name.text.strip()
            if name:
                popup.dismiss()
                self.manager.get_screen('materials').init_new_project(name)
                self.manager.current = 'materials'
        btn_ok.bind(on_release=confirm_create)
        popup.open()

    def open_project(self, project_id):
        calc_screen = self.manager.get_screen('calculation')
        calc_screen.load_existing_project(project_id)
        self.manager.current = 'calculation'

class MaterialsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_name = ""; self.base_materials = ["Розетка", "Лічильник", "LED", "Трансформатор", "Витяжка"]; self.checkboxes = {}
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        self.search_input = ModernTextInput(hint_text="Пошук матеріалів...")
        self.search_input.bind(text=self.on_search_change)
        layout.add_widget(self.search_input)
        self.scroll = ScrollView(do_scroll_x=False)
        self.materials_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.materials_list.bind(minimum_height=self.materials_list.setter('height'))
        self.scroll.add_widget(self.materials_list)
        layout.add_widget(self.scroll)
        self.btn_ok = ModernButton(text="ОК")
        self.btn_ok.bind(on_release=self.proceed_to_calculation)
        layout.add_widget(self.btn_ok)
        self.add_widget(layout)

    def init_new_project(self, name):
        self.project_name = name; self.search_input.text = ""; self.checkboxes.clear(); self.render_materials("")

    def on_search_change(self, instance, value): self.render_materials(value)

    def render_materials(self, query):
        states = {name: cb.active for name, cb in self.checkboxes.items()}
        self.materials_list.clear_widgets(); self.checkboxes.clear()
        for m in self.base_materials:
            if query.lower() in m.lower():
                cb = ModernCheckbox(text=m)
                if m in states: cb.active = states[m]
                self.checkboxes[m] = cb; self.materials_list.add_widget(cb)

    def proceed_to_calculation(self, instance):
        selected_materials = [name for name, cb in self.checkboxes.items() if cb.active]
        if selected_materials:
            calc_screen = self.manager.get_screen('calculation')
            calc_screen.setup_new_calculation(self.project_name, selected_materials)
            self.manager.current = 'calculation'

class CalculationItemWidget(BoxLayout):
    def __init__(self, name, qty=1.0, price=0.0, on_change_callback=None, on_delete_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'; self.size_hint_y = None; self.height = 85; self.spacing = 0; self.material_name = name; self.on_change = on_change_callback
        with self.canvas.before:
            Color(0.94, 0.94, 0.96, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # 1. Заголовок (Назва + хрестик)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, padding=[12, 0, 12, 0])
        lbl_name = Label(text=name, color=[0.1, 0.1, 0.1, 1], font_size='15sp', bold=True, halign='left', valign='middle')
        lbl_name.bind(size=lbl_name.setter('text_size'))
        btn_del = Button(size_hint=(None, None), size=(24, 24), background_normal='', background_color=[0,0,0,0])
        def draw_cross(instance, *args):
            instance.canvas.after.clear()
            with instance.canvas.after:
                Color(0.85, 0.2, 0.2, 1); Line(points=[instance.x + 5, instance.y + 5, instance.right - 5, instance.top - 5], width=1.5); Line(points=[instance.x + 5, instance.top - 5, instance.right - 5, instance.y + 5], width=1.5)
        btn_del.bind(pos=draw_cross, size=draw_cross); btn_del.bind(on_release=lambda inst: on_delete_callback(self))
        header.add_widget(lbl_name); header.add_widget(btn_del); self.add_widget(header)

        # 2. Рядок вводу (Кількість х Ціна грн = Сума)
        calc_row = BoxLayout(orientation='horizontal', spacing=5, padding=[10, 0, 10, 10], size_hint_y=None, height=50)
        
        self.txt_qty = ModernTextInput(text=f"{qty:.3f}".rstrip('0').rstrip('.'), size_hint_x=0.25)
        self.txt_qty.bind(text=self.trigger_recalc)
        
        self.txt_price = ModernTextInput(text=f"{price:.3f}".rstrip('0').rstrip('.'), size_hint_x=0.25)
        self.txt_price.bind(text=self.trigger_recalc)
        
        self.lbl_res = Label(text="0.000", color=[0.1, 0.7, 0.2, 1], font_size='16sp', bold=True, size_hint_x=0.3)
        
        calc_row.add_widget(self.txt_qty)
        calc_row.add_widget(Label(text="×", size_hint_x=0.05, color=[0.5,0.5,0.5,1]))
        calc_row.add_widget(self.txt_price)
        calc_row.add_widget(Label(text="грн", size_hint_x=0.15, color=[0.5,0.5,0.5,1], font_size='12sp'))
        calc_row.add_widget(Label(text="=", size_hint_x=0.05, color=[0.5,0.5,0.5,1]))
        calc_row.add_widget(self.lbl_res)
        
        self.add_widget(calc_row); self.calculate_item_total()

    def _update_bg(self, instance, value): self.bg_rect.pos = self.pos; self.bg_rect.size = self.size
    def trigger_recalc(self, instance, value): self.calculate_item_total(); self.on_change()
    def calculate_item_total(self):
        try: qty = float(self.txt_qty.text) if self.txt_qty.text else 0.0
        except: qty = 0.0
        try: price = float(self.txt_price.text) if self.txt_price.text else 0.0
        except: price = 0.0
        self.lbl_res.text = f"{qty*price:.3f}"; return qty*price
    def get_data(self):
        try: qty = float(self.txt_qty.text) if self.txt_qty.text else 0.0
        except: qty = 0.0
        try: price = float(self.txt_price.text) if self.txt_price.text else 0.0
        except: price = 0.0
        return {"name": self.material_name, "quantity": qty, "price": price, "item_sum": qty * price}

class CalculationScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db = db_manager; self.project_id = None; self.project_name = ""
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.lbl_title = Label(text="Проєкт", color=[0.1, 0.1, 0.1, 1], font_size='18sp', bold=True, halign='center', valign='middle')
        self.lbl_title.bind(size=self.lbl_title.setter('text_size')); header_layout.add_widget(self.lbl_title)
        btn_photo = FlatButton(text="📷 Скрін", size_hint_x=None, width=85)
        btn_photo.bind(on_release=self.take_full_screenshot); header_layout.add_widget(btn_photo); layout.add_widget(header_layout)
        self.scroll = ScrollView(do_scroll_x=False); self.items_container = GridLayout(cols=1, spacing=12, size_hint_y=None)
        self.items_container.bind(minimum_height=self.items_container.setter('height')); self.scroll.add_widget(self.items_container); layout.add_widget(self.scroll)
        add_more_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.txt_new_material = ModernTextInput(hint_text="Назва нового матеріалу"); btn_add_custom = ModernButton(text="+ Додати", size_hint_x=None, width=90)
        btn_add_custom.bind(on_release=self.add_custom_item); add_more_layout.add_widget(self.txt_new_material); add_more_layout.add_widget(btn_add_custom); layout.add_widget(add_more_layout)
        self.lbl_total = Label(text="Загальна сума: 0.000", color=[0.1, 0.1, 0.1, 1], font_size='17sp', bold=True, size_hint_y=None, height=30, halign='right')
        self.lbl_total.bind(size=self.lbl_total.setter('text_size')); layout.add_widget(self.lbl_total)
        btn_save = ModernButton(text="Зберегти та вийти"); btn_save.bind(on_release=self.save_and_exit); layout.add_widget(btn_save); self.add_widget(layout)

    def setup_new_calculation(self, name, materials):
        self.project_id = None; self.project_name = name; self.lbl_title.text = f"Проєкт: {name}"; self.items_container.clear_widgets()
        for m in materials: self.items_container.add_widget(CalculationItemWidget(m, on_change_callback=self.update_total_sum, on_delete_callback=self.delete_item))
        Clock.schedule_once(lambda dt: self.update_total_sum(), 0.1)

    def load_existing_project(self, project_id):
        self.project_id = project_id; data = self.db.get_project_details(project_id)
        if data:
            self.project_name = data["name"]; self.lbl_title.text = f"Проєкт: {data['name']}"; self.items_container.clear_widgets()
            for item in data["items"]: self.items_container.add_widget(CalculationItemWidget(item["name"], qty=item["quantity"], price=item["price"], on_change_callback=self.update_total_sum, on_delete_callback=self.delete_item))
            Clock.schedule_once(lambda dt: self.update_total_sum(), 0.1)

    def add_custom_item(self, instance):
        name = self.txt_new_material.text.strip()
        if name: self.items_container.add_widget(CalculationItemWidget(name, on_change_callback=self.update_total_sum, on_delete_callback=self.delete_item)); self.txt_new_material.text = ""; self.update_total_sum()

    def delete_item(self, item_widget): self.items_container.remove_widget(item_widget); self.update_total_sum()

    def update_total_sum(self, *args):
        total = sum(c.calculate_item_total() for c in self.items_container.children if isinstance(c, CalculationItemWidget))
        self.lbl_total.text = f"Загальна сума: {total:.3f}"

    def save_and_exit(self, instance):
        items = [c.get_data() for c in self.items_container.children if isinstance(c, CalculationItemWidget)]
        self.db.save_project(self.project_name, items, sum(i['item_sum'] for i in items), self.project_id); self.manager.current = 'main'

    def take_full_screenshot(self, instance):
        export_layout = BoxLayout(orientation='vertical', size_hint=(None, None), width=self.width, padding=20, spacing=15)
        export_layout.height = 140 + self.items_container.height
        with export_layout.canvas.before:
            Color(0.98, 0.98, 0.98, 1); self.export_bg = Rectangle(pos=export_layout.pos, size=export_layout.size)
        export_layout.bind(pos=lambda i, v: setattr(self.export_bg, 'pos', i.pos), size=lambda i, v: setattr(self.export_bg, 'size', i.size))
        title_lbl = Label(text=f"Проєкт: {self.project_name}", color=[0.1, 0.1, 0.1, 1], font_size='22sp', bold=True, size_hint_y=None, height=50)
        export_layout.add_widget(title_lbl); self.scroll.remove_widget(self.items_container); export_layout.add_widget(self.items_container)
        export_layout.add_widget(Label(text=self.lbl_total.text, color=[0.1, 0.1, 0.1, 1], font_size='18sp', bold=True, size_hint_y=None, height=50)); export_layout.x = 5000; self.add_widget(export_layout); export_layout.do_layout()
        def _export(*args):
            temp_file = "temp_screenshot.png"; export_layout.export_to_png(temp_file); self.remove_widget(export_layout); export_layout.remove_widget(self.items_container); self.scroll.add_widget(self.items_container)
            if platform == 'android':
                try: shutil.move(temp_file, os.path.join('/storage/emulated/0/Pictures', f"Кошторис_{self.project_name}_{int(time.time())}.png")); self.show_success_popup("Збережено у Галерею!")
                except: self.show_success_popup("Помилка доступу до пам'яті.")
            else: self.show_save_dialog_pc(temp_file, f"Кошторис_{self.project_name}.png")
        Clock.schedule_once(_export, 0.2)

    def show_save_dialog_pc(self, temp_file, default_name):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10); fc = FileChooserListView(path=os.path.expanduser('~')); content.add_widget(fc)
        btn = ModernButton(text="Зберегти"); btn.bind(on_release=lambda x: (shutil.move(temp_file, os.path.join(fc.path, default_name)), p.dismiss(), self.show_success_popup("Збережено!"))); content.add_widget(btn); p = Popup(title="Виберіть папку", content=content, size_hint=(0.9, 0.9)); p.open()

    def show_success_popup(self, msg):
        content = BoxLayout(orientation='vertical', padding=10); content.add_widget(Label(text=msg, color=[0,0,0,1])); btn = ModernButton(text="ОК"); p = Popup(title="Інфо", content=content, size_hint=(0.8, 0.3)); btn.bind(on_release=p.dismiss); content.add_widget(btn); p.open()