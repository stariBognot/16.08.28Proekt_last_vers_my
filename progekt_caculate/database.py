import os
import sqlite3

from kivy.app import App


class DatabaseManager:
    def __init__(self, db_name="projects_calc.db"):
        app = App.get_running_app()

        if app:
            os.makedirs(app.user_data_dir, exist_ok=True)
            self.db_path = os.path.join(app.user_data_dir, db_name)
        else:
            self.db_path = os.path.abspath(db_name)

        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    total_sum REAL NOT NULL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    material_name TEXT NOT NULL,
                    quantity REAL NOT NULL DEFAULT 0,
                    price REAL NOT NULL DEFAULT 0,
                    item_sum REAL NOT NULL DEFAULT 0,
                    FOREIGN KEY (project_id)
                        REFERENCES projects(id)
                        ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def get_all_projects(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, total_sum
                FROM projects
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "total_sum": row[2]
                }
                for row in rows
            ]

    def get_project_details(self, project_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, total_sum
                FROM projects
                WHERE id = ?
            """, (project_id,))

            project_row = cursor.fetchone()

            if not project_row:
                return None

            cursor.execute("""
                SELECT material_name, quantity, price, item_sum
                FROM project_items
                WHERE project_id = ?
                ORDER BY id ASC
            """, (project_id,))

            items_rows = cursor.fetchall()

            items = [
                {
                    "name": row[0],
                    "quantity": row[1],
                    "price": row[2],
                    "item_sum": row[3]
                }
                for row in items_rows
            ]

            return {
                "id": project_row[0],
                "name": project_row[1],
                "total_sum": project_row[2],
                "items": items
            }

    def save_project(self, name, items, total_sum, project_id=None):
        name = name.strip()

        if not name:
            raise ValueError("Назва проєкту не може бути порожньою.")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            if project_id is not None:
                cursor.execute("""
                    UPDATE projects
                    SET name = ?, total_sum = ?
                    WHERE id = ?
                """, (name, total_sum, project_id))

                cursor.execute("""
                    DELETE FROM project_items
                    WHERE project_id = ?
                """, (project_id,))
            else:
                cursor.execute("""
                    INSERT INTO projects (name, total_sum)
                    VALUES (?, ?)
                """, (name, total_sum))

                project_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO project_items (
                        project_id,
                        material_name,
                        quantity,
                        price,
                        item_sum
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project_id,
                    item["name"],
                    item["quantity"],
                    item["price"],
                    item["item_sum"]
                ))

            conn.commit()

            return project_id

    def delete_project(self, project_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM projects
                WHERE id = ?
            """, (project_id,))

            conn.commit()

    def get_custom_materials(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name
                FROM custom_materials
                ORDER BY name COLLATE NOCASE ASC
            """)

            return [
                {
                    "id": row[0],
                    "name": row[1]
                }
                for row in cursor.fetchall()
            ]

    def add_custom_material(self, name):
        name = name.strip()

        if not name:
            raise ValueError("Назва матеріалу не може бути порожньою.")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO custom_materials (name)
                    VALUES (?)
                """, (name,))
                conn.commit()
                return True

            except sqlite3.IntegrityError:
                return False

    def delete_custom_material(self, material_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM custom_materials
                WHERE id = ?
            """, (material_id,))

            conn.commit()
