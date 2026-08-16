import os
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from widgets import (
    DangerButton,
    FlatButton,
    ModernButton,
    ModernCheckbox,
    ModernTextInput
)


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        self.root_layout = BoxLayout(
            orientation="vertical"
        )

        self.navigation_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            spacing=dp(8)
        )

        self.btn_back = FlatButton(
            text="← Назад",
            size_hint_x=None,
            width=dp(105)
        )

        self.btn_forward = FlatButton(
            text="Вперед →",
            size_hint_x=None,
            width=dp(115)
        )

        self.nav_title = Label(
            text="",
            color=[0.15, 0.15, 0.15, 1],
            font_size="15sp",
            bold=True,
            halign="center",
            valign="middle"
        )

        self.nav_title.bind(
            size=self.nav_title.setter("text_size")
        )

        self.btn_back.bind(
            on_release=lambda _instance: App.get_running_app().go_back()
        )

        self.btn_forward.bind(
            on_release=lambda _instance: App.get_running_app().go_forward()
        )

        self.navigation_bar.add_widget(self.btn_back)
        self.navigation_bar.add_widget(self.nav_title)
        self.navigation_bar.add_widget(self.btn_forward)

        self.content = BoxLayout(
            orientation="vertical"
        )

        self.root_layout.add_widget(self.navigation_bar)
        self.root_layout.add_widget(self.content)

        self.add_widget(self.root_layout)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_pre_enter(self, *args):
        app = App.get_running_app()

        if app:
            self.btn_back.disabled = not app.can_go_back()
            self.btn_forward.disabled = not app.can_go_forward()

    def ensure_visible(self, widget):
        scroll = getattr(self, "scroll", None)

        if scroll:
            Clock.schedule_once(
                lambda _dt: scroll.scroll_to(
                    widget,
                    padding=dp(90),
                    animate=True
                ),
                0.1
            )


class MainScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)

        self.db = db_manager
        self.all_projects = []

        self.nav_title.text = "Мої чеки"

        main_layout = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12)
        )

        self.search_input = ModernTextInput(
            hint_text="Пошук чеків..."
        )

        self.search_input.bind(
            text=self.on_search_change
        )

        main_layout.add_widget(self.search_input)

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(6)
        )

        self.projects_list = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(3), 0, dp(8)]
        )

        self.projects_list.bind(
            minimum_height=self.projects_list.setter("height")
        )

        self.scroll.add_widget(self.projects_list)

        main_layout.add_widget(self.scroll)

        btn_add = ModernButton(
            text="+ Додати чек"
        )

        btn_add.bind(
            on_release=self.show_create_popup
        )

        main_layout.add_widget(btn_add)

        self.content.add_widget(main_layout)

    def on_enter(self):
        self.refresh_projects()

    def refresh_projects(self):
        self.all_projects = self.db.get_all_projects()
        self.filter_projects(self.search_input.text)

    def on_search_change(self, _instance, value):
        self.filter_projects(value)

    def filter_projects(self, query):
        query = query.lower().strip()

        self.projects_list.clear_widgets()

        for project in self.all_projects:
            if query not in project["name"].lower():
                continue

            card = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(68),
                spacing=dp(8),
                padding=[dp(10), dp(8), dp(8), dp(8)]
            )

            with card.canvas.before:
                Color(0.92, 0.92, 0.95, 1)
                bg = RoundedRectangle(
                    pos=card.pos,
                    size=card.size,
                    radius=[dp(10)]
                )

            card.bind(
                pos=lambda instance, _value: setattr(bg, "pos", instance.pos),
                size=lambda instance, _value: setattr(bg, "size", instance.size)
            )

            open_button = Button(
                text=(
                    f"{project['name']}\n"
                    f"Сума: {project['total_sum']:.3f} грн"
                ),
                background_normal="",
                background_down="",
                background_color=[0, 0, 0, 0],
                color=[0.1, 0.1, 0.1, 1],
                font_size="16sp",
                halign="left",
                valign="middle"
            )

            open_button.bind(
                size=open_button.setter("text_size")
            )

            open_button.bind(
                on_release=lambda _instance, pid=project["id"]:
                self.open_project(pid)
            )

            delete_button = DangerButton(
                text="🗑",
                size_hint_x=None,
                width=dp(54)
            )

            delete_button.bind(
                on_release=lambda _instance, p=project:
                self.confirm_delete_project(p)
            )

            card.add_widget(open_button)
            card.add_widget(delete_button)

            self.projects_list.add_widget(card)

    def show_create_popup(self, _instance):
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(14)
        )

        label = Label(
            text="Введіть назву нового чека:",
            color=[0.1, 0.1, 0.1, 1],
            font_size="16sp"
        )

        txt_name = ModernTextInput(
            hint_text="Наприклад: Квартира №12"
        )

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        btn_cancel = FlatButton(text="Скасувати")
        btn_ok = ModernButton(text="Створити")

        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_ok)

        content.add_widget(label)
        content.add_widget(txt_name)
        content.add_widget(buttons)

        popup = Popup(
            title="Новий чек",
            content=content,
            size_hint=(0.90, None),
            height=dp(245),
            auto_dismiss=False
        )

        btn_cancel.bind(on_release=popup.dismiss)

        def confirm_create(_button):
            name = txt_name.text.strip()

            if not name:
                txt_name.focus = True
                return

            popup.dismiss()

            materials_screen = self.manager.get_screen("materials")
            materials_screen.init_new_project(name)

            App.get_running_app().navigate("materials")

        btn_ok.bind(on_release=confirm_create)

        popup.open()

        Clock.schedule_once(
            lambda _dt: setattr(txt_name, "focus", True),
            0.2
        )

    def confirm_delete_project(self, project):
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(14)
        )

        message = Label(
            text=(
                f'Ви точно хочете видалити чек\n'
                f'"{project["name"]}"?'
            ),
            color=[0.1, 0.1, 0.1, 1],
            font_size="16sp",
            halign="center",
            valign="middle"
        )

        message.bind(size=message.setter("text_size"))

        buttons = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        btn_no = FlatButton(text="Ні")
        btn_yes = DangerButton(text="Так")

        buttons.add_widget(btn_no)
        buttons.add_widget(btn_yes)

        content.add_widget(message)
        content.add_widget(buttons)

        popup = Popup(
            title="Підтвердження видалення",
            content=content,
            size_hint=(0.88, None),
            height=dp(220),
            auto_dismiss=False
        )

        btn_no.bind(on_release=popup.dismiss)

        def delete_project(_button):
            self.db.delete_project(project["id"])
            popup.dismiss()
            self.refresh_projects()

        btn_yes.bind(on_release=delete_project)

        popup.open()

    def open_project(self, project_id):
        calculation_screen = self.manager.get_screen("calculation")
        calculation_screen.load_existing_project(project_id)

        App.get_running_app().navigate("calculation")


class MaterialsScreen(BaseScreen):
    DEFAULT_MATERIALS = [
        "Розетка",
        "Лічильник",
        "LED",
        "Трансформатор",
        "Витяжка"
    ]

    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)

        self.db = db_manager
        self.project_name = ""
        self.selected_materials = set()
        self.current_materials = []

        self.nav_title.text = "Матеріали"

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12)
        )

        self.search_input = ModernTextInput(
            hint_text="Пошук матеріалів..."
        )

        self.search_input.bind(
            text=self.on_search_change
        )

        layout.add_widget(self.search_input)

        add_layout = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        self.new_material_input = ModernTextInput(
            hint_text="Новий матеріал"
        )

        btn_add_material = ModernButton(
            text="+ Додати",
            size_hint_x=None,
            width=dp(112)
        )

        btn_add_material.bind(
            on_release=self.add_custom_material
        )

        add_layout.add_widget(self.new_material_input)
        add_layout.add_widget(btn_add_material)

        layout.add_widget(add_layout)

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(6)
        )

        self.materials_list = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=[0, dp(3), 0, dp(8)]
        )

        self.materials_list.bind(
            minimum_height=self.materials_list.setter("height")
        )

        self.scroll.add_widget(self.materials_list)

        layout.add_widget(self.scroll)

        self.btn_ok = ModernButton(
            text="Продовжити"
        )

        self.btn_ok.bind(
            on_release=self.proceed_to_calculation
        )

        layout.add_widget(self.btn_ok)

        self.content.add_widget(layout)

    def init_new_project(self, name):
        self.project_name = name
        self.selected_materials.clear()
        self.search_input.text = ""
        self.new_material_input.text = ""
        self.refresh_materials()

    def get_all_materials(self):
        custom_materials = self.db.get_custom_materials()

        result = []

        for material in self.DEFAULT_MATERIALS:
            result.append({
                "id": None,
                "name": material,
                "is_custom": False
            })

        for material in custom_materials:
            result.append({
                "id": material["id"],
                "name": material["name"],
                "is_custom": True
            })

        return result

    def refresh_materials(self):
        self.current_materials = self.get_all_materials()
        self.render_materials(self.search_input.text)

    def on_search_change(self, _instance, value):
        self.render_materials(value)

    def render_materials(self, query):
        query = query.lower().strip()

        self.materials_list.clear_widgets()

        for material in self.current_materials:
            if query not in material["name"].lower():
                continue

            row = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(54)
            )

            checkbox = ModernCheckbox(
                text=material["name"],
                active=material["name"] in self.selected_materials
            )

            def update_selection(instance, active, material_name=material["name"]):
                if active:
                    self.selected_materials.add(material_name)
                else:
                    self.selected_materials.discard(material_name)

            checkbox.bind(active=update_selection)

            row.add_widget(checkbox)

            if material["is_custom"]:
                delete_button = DangerButton(
                    text="🗑",
                    size_hint_x=None,
                    width=dp(54)
                )

                delete_button.bind(
                    on_release=lambda _button, m=material:
                    self.confirm_delete_custom_material(m)
                )

                row.add_widget(delete_button)

            self.materials_list.add_widget(row)

    def add_custom_material(self, _instance):
        name = self.new_material_input.text.strip()

        if not name:
            self.new_material_input.focus = True
            return

        added = self.db.add_custom_material(name)

        if added:
            self.selected_materials.add(name)
            self.new_material_input.text = ""
            self.refresh_materials()
        else:
            self.show_info_popup(
                "Такий матеріал уже існує."
            )

    def confirm_delete_custom_material(self, material):
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(14)
        )

        label = Label(
            text=(
                f'Ви точно хочете видалити матеріал\n'
                f'"{material["name"]}"?'
            ),
            color=[0.1, 0.1, 0.1, 1],
            font_size="16sp",
            halign="center",
            valign="middle"
        )

        label.bind(size=label.setter("text_size"))

        buttons = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        btn_no = FlatButton(text="Ні")
        btn_yes = DangerButton(text="Так")

        buttons.add_widget(btn_no)
        buttons.add_widget(btn_yes)

        content.add_widget(label)
        content.add_widget(buttons)

        popup = Popup(
            title="Видалення матеріалу",
            content=content,
            size_hint=(0.88, None),
            height=dp(220),
            auto_dismiss=False
        )

        btn_no.bind(on_release=popup.dismiss)

        def delete_material(_button):
            self.db.delete_custom_material(material["id"])
            self.selected_materials.discard(material["name"])
            popup.dismiss()
            self.refresh_materials()

        btn_yes.bind(on_release=delete_material)

        popup.open()

    def proceed_to_calculation(self, _instance):
        selected = list(self.selected_materials)

        if not selected:
            self.show_info_popup(
                "Виберіть хоча б один матеріал."
            )
            return

        calc_screen = self.manager.get_screen("calculation")
        calc_screen.setup_new_calculation(
            self.project_name,
            selected
        )

        App.get_running_app().navigate("calculation")

    def show_info_popup(self, message):
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(14)
        )

        content.add_widget(
            Label(
                text=message,
                color=[0.1, 0.1, 0.1, 1],
                font_size="16sp"
            )
        )

        button = ModernButton(text="OK")

        content.add_widget(button)

        popup = Popup(
            title="Інформація",
            content=content,
            size_hint=(0.82, None),
            height=dp(180)
        )

        button.bind(on_release=popup.dismiss)

        popup.open()


class CalculationItemWidget(BoxLayout):
    def __init__(
        self,
        name,
        qty=1.0,
        price=0.0,
        on_change_callback=None,
        on_delete_callback=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(104)
        self.spacing = dp(2)

        self.material_name = name
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback

        with self.canvas.before:
            Color(0.94, 0.94, 0.96, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

        self.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            padding=[dp(12), 0, dp(6), 0]
        )

        lbl_name = Label(
            text=name,
            color=[0.1, 0.1, 0.1, 1],
            font_size="16sp",
            bold=True,
            halign="left",
            valign="middle"
        )

        lbl_name.bind(size=lbl_name.setter("text_size"))

        btn_delete = Button(
            text="✕",
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            color=[0.82, 0.20, 0.20, 1],
            font_size="22sp"
        )

        btn_delete.bind(
            on_release=lambda _instance:
            self.on_delete_callback(self)
        )

        header.add_widget(lbl_name)
        header.add_widget(btn_delete)

        self.add_widget(header)

        calc_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(5),
            padding=[dp(10), 0, dp(10), dp(10)],
            size_hint_y=None,
            height=dp(56)
        )

        self.txt_qty = ModernTextInput(
            text=f"{qty:.3f}".rstrip("0").rstrip("."),
            input_filter="float",
            hint_text="К-сть",
            size_hint_x=0.28
        )

        self.txt_price = ModernTextInput(
            text=f"{price:.3f}".rstrip("0").rstrip("."),
            input_filter="float",
            hint_text="Ціна",
            size_hint_x=0.28
        )

        self.txt_qty.bind(text=self.trigger_recalc)
        self.txt_price.bind(text=self.trigger_recalc)

        self.lbl_res = Label(
            text="0.000",
            color=[0.1, 0.65, 0.20, 1],
            font_size="16sp",
            bold=True,
            size_hint_x=0.25,
            halign="center",
            valign="middle"
        )

        self.lbl_res.bind(
            size=self.lbl_res.setter("text_size")
        )

        calc_row.add_widget(self.txt_qty)
        calc_row.add_widget(
            Label(
                text="×",
                size_hint_x=0.07,
                color=[0.45, 0.45, 0.45, 1]
            )
        )

        calc_row.add_widget(self.txt_price)
        calc_row.add_widget(
            Label(
                text="=",
                size_hint_x=0.07,
                color=[0.45, 0.45, 0.45, 1]
            )
        )

        calc_row.add_widget(self.lbl_res)

        self.add_widget(calc_row)

        self.calculate_item_total()

    def _update_bg(self, _instance, _value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def trigger_recalc(self, _instance, _value):
        self.calculate_item_total()

        if self.on_change_callback:
            self.on_change_callback()

    def parse_number(self, value):
        try:
            return float(value.replace(",", ".")) if value else 0.0
        except ValueError:
            return 0.0

    def calculate_item_total(self):
        qty = self.parse_number(self.txt_qty.text)
        price = self.parse_number(self.txt_price.text)

        total = qty * price

        self.lbl_res.text = f"{total:.3f}"

        return total

    def get_data(self):
        qty = self.parse_number(self.txt_qty.text)
        price = self.parse_number(self.txt_price.text)

        return {
            "name": self.material_name,
            "quantity": qty,
            "price": price,
            "item_sum": qty * price
        }


class CalculationScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)

        self.db = db_manager
        self.project_id = None
        self.project_name = ""

        self.nav_title.text = "Розрахунок"

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12)
        )

        header_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44)
        )

        self.lbl_title = Label(
            text="Чек",
            color=[0.1, 0.1, 0.1, 1],
            font_size="19sp",
            bold=True,
            halign="left",
            valign="middle"
        )

        self.lbl_title.bind(
            size=self.lbl_title.setter("text_size")
        )

        btn_photo = FlatButton(
            text="📷 PNG",
            size_hint_x=None,
            width=dp(90)
        )

        btn_photo.bind(
            on_release=self.take_full_screenshot
        )

        header_layout.add_widget(self.lbl_title)
        header_layout.add_widget(btn_photo)

        layout.add_widget(header_layout)

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(6)
        )

        self.items_container = GridLayout(
            cols=1,
            spacing=dp(12),
            size_hint_y=None,
            padding=[0, dp(3), 0, dp(8)]
        )

        self.items_container.bind(
            minimum_height=self.items_container.setter("height")
        )

        self.scroll.add_widget(self.items_container)

        layout.add_widget(self.scroll)

        add_more_layout = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        self.txt_new_material = ModernTextInput(
            hint_text="Назва нового матеріалу"
        )

        btn_add_custom = ModernButton(
            text="+ Додати",
            size_hint_x=None,
            width=dp(112)
        )

        btn_add_custom.bind(
            on_release=self.add_custom_item
        )

        add_more_layout.add_widget(self.txt_new_material)
        add_more_layout.add_widget(btn_add_custom)

        layout.add_widget(add_more_layout)

        self.lbl_total = Label(
            text="Загальна сума: 0.000 грн",
            color=[0.1, 0.1, 0.1, 1],
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height=dp(36),
            halign="right",
            valign="middle"
        )

        self.lbl_total.bind(
            size=self.lbl_total.setter("text_size")
        )

        layout.add_widget(self.lbl_total)

        btn_save = ModernButton(
            text="Зберегти та вийти"
        )

        btn_save.bind(
            on_release=self.save_and_exit
        )

        layout.add_widget(btn_save)

        self.content.add_widget(layout)

    def setup_new_calculation(self, name, materials):
        self.project_id = None
        self.project_name = name
        self.lbl_title.text = f"Чек: {name}"

        self.items_container.clear_widgets()

        for material in materials:
            self.add_item_widget(material)

        Clock.schedule_once(
            lambda _dt: self.update_total_sum(),
            0.1
        )

    def load_existing_project(self, project_id):
        self.project_id = project_id

        data = self.db.get_project_details(project_id)

        if not data:
            return

        self.project_name = data["name"]
        self.lbl_title.text = f"Чек: {self.project_name}"

        self.items_container.clear_widgets()

        for item in data["items"]:
            self.add_item_widget(
                item["name"],
                item["quantity"],
                item["price"]
            )

        Clock.schedule_once(
            lambda _dt: self.update_total_sum(),
            0.1
        )

    def add_item_widget(self, name, qty=1.0, price=0.0):
        widget = CalculationItemWidget(
            name,
            qty=qty,
            price=price,
            on_change_callback=self.update_total_sum,
            on_delete_callback=self.delete_item
        )

        self.items_container.add_widget(widget)

    def add_custom_item(self, _instance):
        name = self.txt_new_material.text.strip()

        if not name:
            self.txt_new_material.focus = True
            return

        self.add_item_widget(name)

        self.txt_new_material.text = ""
        self.update_total_sum()

        Clock.schedule_once(
            lambda _dt: self.scroll.scroll_to(
                self.items_container.children[0],
                padding=dp(80),
                animate=True
            ),
            0.1
        )

    def delete_item(self, item_widget):
        self.items_container.remove_widget(item_widget)
        self.update_total_sum()

    def update_total_sum(self, *args):
        total = 0.0

        for child in self.items_container.children:
            if isinstance(child, CalculationItemWidget):
                total += child.calculate_item_total()

        self.lbl_total.text = f"Загальна сума: {total:.3f} грн"

    def get_items_data(self):
        items = []

        for child in reversed(self.items_container.children):
            if isinstance(child, CalculationItemWidget):
                items.append(child.get_data())

        return items

    def save_and_exit(self, _instance):
        items = self.get_items_data()

        total_sum = sum(
            item["item_sum"]
            for item in items
        )

        self.project_id = self.db.save_project(
            self.project_name,
            items,
            total_sum,
            self.project_id
        )

        App.get_running_app().navigate("main")

    def take_full_screenshot(self, _instance):
        export_layout = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=self.width,
            padding=dp(20),
            spacing=dp(12)
        )

        export_layout.height = dp(120) + len(
            self.items_container.children
        ) * dp(46)

        with export_layout.canvas.before:
            Color(0.98, 0.98, 0.98, 1)

            export_bg = Rectangle(
                pos=export_layout.pos,
                size=export_layout.size
            )

        export_layout.bind(
            pos=lambda instance, _value:
            setattr(export_bg, "pos", instance.pos),
            size=lambda instance, _value:
            setattr(export_bg, "size", instance.size)
        )

        title = Label(
            text=f"Чек: {self.project_name}",
            color=[0.1, 0.1, 0.1, 1],
            font_size="21sp",
            bold=True,
            size_hint_y=None,
            height=dp(44)
        )

        export_layout.add_widget(title)

        for item in self.get_items_data():
            export_layout.add_widget(
                Label(
                    text=(
                        f'{item["name"]}: '
                        f'{item["quantity"]:.3f} × '
                        f'{item["price"]:.3f} = '
                        f'{item["item_sum"]:.3f} грн'
                    ),
                    color=[0.1, 0.1, 0.1, 1],
                    font_size="15sp",
                    size_hint_y=None,
                    height=dp(36),
                    halign="left",
                    valign="middle"
                )
            )

        export_layout.add_widget(
            Label(
                text=self.lbl_total.text,
                color=[0.1, 0.1, 0.1, 1],
                font_size="18sp",
                bold=True,
                size_hint_y=None,
                height=dp(42)
            )
        )

        export_layout.x = Window.width + dp(100)

        self.add_widget(export_layout)

        def export_png(_dt):
            app = App.get_running_app()

            screenshots_dir = os.path.join(
                app.user_data_dir,
                "screenshots"
            )

            os.makedirs(screenshots_dir, exist_ok=True)

            safe_name = "".join(
                char if char.isalnum() or char in (" ", "_", "-")
                else "_"
                for char in self.project_name
            )

            file_name = (
                f"Кошторис_{safe_name}_{int(time.time())}.png"
            )

            file_path = os.path.join(
                screenshots_dir,
                file_name
            )

            export_layout.export_to_png(file_path)

            self.remove_widget(export_layout)

            self.show_info_popup(
                "PNG збережено у внутрішній папці застосунку:\n"
                f"{file_name}"
            )

        Clock.schedule_once(export_png, 0.3)

    def show_info_popup(self, message):
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(14)
        )

        label = Label(
            text=message,
            color=[0.1, 0.1, 0.1, 1],
            font_size="15sp",
            halign="center",
            valign="middle"
        )

        label.bind(size=label.setter("text_size"))

        button = ModernButton(text="OK")

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title="Інформація",
            content=content,
            size_hint=(0.86, None),
            height=dp(220)
        )

        button.bind(on_release=popup.dismiss)

        popup.open()
