import sqlite3
import json
import os
from kivy.app import App

class DatabaseManager:
    def __init__(self, db_name="projects_calc.db"):
        # Перевіряємо, чи запущено додаток (потрібно для Android)
        app = App.get_running_app()
        if app:
            # На Android user_data_dir веде у спеціальну внутрішню папку, де дозволено писати файли
            self.db_path = os.path.join(app.user_data_dir, db_name)
        else:
            # На випадок, якщо ви запускаєте цей скрипт окремо поза Kivy (наприклад, для тестів)
            self.db_path = db_name
            
        self.init_db()

    def get_connection(self):
        # Підключаємося за абсолютним правильним шляхом
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Таблиця проєктів
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    total_sum REAL NOT NULL
                )
            """)
            # Таблиця матеріалів у проєкті
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    material_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    item_sum REAL NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def get_all_projects(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, total_sum FROM projects ORDER BY id DESC")
            rows = cursor.fetchall()
            return [{"id": r[0], "name": r[1], "total_sum": r[2]} for r in rows]

    def get_project_details(self, project_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, total_sum FROM projects WHERE id = ?", (project_id,))
            project_row = cursor.fetchone()
            if not project_row:
                return None
            
            cursor.execute("""
                SELECT material_name, quantity, price, item_sum 
                FROM project_items WHERE project_id = ?
            """, (project_id,))
            items_rows = cursor.fetchall()
            
            items = []
            for item in items_rows:
                items.append({
                    "name": item[0],
                    "quantity": item[1],
                    "price": item[2],
                    "item_sum": item[3]
                })
                
            return {
                "id": project_id,
                "name": project_row[0],
                "total_sum": project_row[1],
                "items": items
            }

    def save_project(self, name, items, total_sum, project_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if project_id:
                # Оновлення існуючого проєкту
                cursor.execute(
                    "UPDATE projects SET name = ?, total_sum = ? WHERE id = ?",
                    (name, total_sum, project_id)
                )
                cursor.execute("DELETE FROM project_items WHERE project_id = ?", (project_id,))
            else:
                # Створення нового проєкту
                cursor.execute(
                    "INSERT INTO projects (name, total_sum) VALUES (?, ?)",
                    (name, total_sum)
                )
                project_id = cursor.lastrowid

            # Вставка елементів проєкту
            for item in items:
                cursor.execute("""
                    INSERT INTO project_items (project_id, material_name, quantity, price, item_sum)
                    VALUES (?, ?, ?, ?, ?)
                """, (project_id, item["name"], item["quantity"], item["price"], item["item_sum"]))
            
            conn.commit()
            return project_id