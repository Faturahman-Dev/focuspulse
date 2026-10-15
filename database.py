"""
database.py
Manajemen Penyimpanan Lokal menggunakan SQLite3.
Menyediakan operasi CRUD untuk Tugas/Kebiasaan serta riwayat sesi Pomodoro.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from models import Task, PomodoroSession

# Nama file database default di direktori yang sama
DB_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "productivity.db")


class DatabaseManager:
    """Pengelola database SQLite lokal aplikasi produktivitas."""

    def __init__(self, db_path: str = DB_FILENAME):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Membuka koneksi ke database SQLite dengan row_factory untuk akses dictionary-like."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _execute(self, query: str, params: tuple = (), fetch: str = "none"):
        """Helper untuk menjalankan query dengan membuka dan menutup koneksi otomatis."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            elif fetch == "lastrowid":
                conn.commit()
                result = cursor.lastrowid
            elif fetch == "rowcount":
                conn.commit()
                result = cursor.rowcount
            else:
                conn.commit()
                result = None
            return result
        finally:
            conn.close()

    def _init_db(self):
        """Membuat tabel jika belum ada dan mengisi data awal jika database masih kosong."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Tabel Tasks & Habits
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    is_completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )

            # Tabel Pomodoro Sessions
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    completed_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

            cursor.execute("SELECT COUNT(*) as count FROM tasks")
            if cursor.fetchone()["count"] == 0:
                self._seed_initial_data(cursor)
                conn.commit()
        finally:
            conn.close()

    def _seed_initial_data(self, cursor: sqlite3.Cursor):
        """Mengisi data contoh agar tampilan dashboard langsung informatif saat pertama dibuka."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_tasks = [
            ("Belajar dasar Flet untuk Mobile", "Belajar", 1, now),
            ("Rapat Evaluasi Sprint Proyek", "Pekerjaan", 0, None),
            ("Minum 2 Liter Air Putih", "Kebiasaan", 1, now),
            ("Olahraga Ringan / Peregangan 15 Menit", "Kebiasaan", 0, None),
            ("Membaca Buku 10 Halaman", "Pribadi", 0, None),
        ]
        for title, category, is_done, done_at in initial_tasks:
            cursor.execute(
                """
                INSERT INTO tasks (title, category, is_completed, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, category, is_done, now, done_at),
            )

    # --- Operasi Tugas & Kebiasaan (Tasks & Habits) ---

    def add_task(self, title: str, category: str) -> int:
        """Menambahkan tugas atau kebiasaan baru ke dalam database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self._execute(
            """
            INSERT INTO tasks (title, category, is_completed, created_at)
            VALUES (?, ?, 0, ?)
            """,
            (title.strip(), category, now),
            fetch="lastrowid",
        )

    def toggle_task(self, task_id: int) -> bool:
        """Mengubah status selesai/belum selesai tugas."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT is_completed FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return False

            new_status = 0 if row["is_completed"] == 1 else 1
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == 1 else None

            cursor.execute(
                """
                UPDATE tasks
                SET is_completed = ?, completed_at = ?
                WHERE id = ?
                """,
                (new_status, completed_at, task_id),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_task(self, task_id: int) -> bool:
        """Menghapus tugas berdasarkan ID."""
        rowcount = self._execute("DELETE FROM tasks WHERE id = ?", (task_id,), fetch="rowcount")
        return rowcount > 0

    def get_tasks(self, category: Optional[str] = None) -> List[Task]:
        """Mengambil daftar tugas, dengan filter kategori opsional."""
        if category and category != "Semua":
            query = """
                SELECT id, title, category, is_completed, created_at, completed_at
                FROM tasks
                WHERE category = ?
                ORDER BY is_completed ASC, id DESC
            """
            rows = self._execute(query, (category,), fetch="all")
        else:
            query = """
                SELECT id, title, category, is_completed, created_at, completed_at
                FROM tasks
                ORDER BY is_completed ASC, id DESC
            """
            rows = self._execute(query, fetch="all")

        return [
            Task(
                id=row["id"],
                title=row["title"],
                category=row["category"],
                is_completed=bool(row["is_completed"]),
                created_at=row["created_at"],
                completed_at=row["completed_at"],
            )
            for row in rows
        ]

    # --- Operasi Sesi Pomodoro ---

    def add_pomodoro_session(self, session_type: str, duration_minutes: int) -> int:
        """Mencatat sesi fokus atau istirahat yang telah diselesaikan."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self._execute(
            """
            INSERT INTO pomodoro_sessions (session_type, duration_minutes, completed_at)
            VALUES (?, ?, ?)
            """,
            (session_type, duration_minutes, now),
            fetch="lastrowid",
        )

    def get_today_pomodoro_sessions(self) -> List[PomodoroSession]:
        """Mengambil daftar sesi Pomodoro yang selesai pada hari ini."""
        today_prefix = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT id, session_type, duration_minutes, completed_at
            FROM pomodoro_sessions
            WHERE completed_at LIKE ?
            ORDER BY id DESC
        """
        rows = self._execute(query, (f"{today_prefix}%",), fetch="all")
        return [
            PomodoroSession(
                id=row["id"],
                session_type=row["session_type"],
                duration_minutes=row["duration_minutes"],
                completed_at=row["completed_at"],
            )
            for row in rows
        ]

    # --- Dashboard Summary ---

    def get_summary(self) -> Dict:
        """Mengumpulkan ringkasan data produktivitas harian untuk Dashboard."""
        today_prefix = datetime.now().strftime("%Y-%m-%d")
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Statistik Tugas
            cursor.execute("SELECT COUNT(*) as total FROM tasks")
            total_tasks = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE is_completed = 1")
            completed_tasks = cursor.fetchone()["completed"]

            pending_tasks = total_tasks - completed_tasks
            completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0

            # Statistik per Kategori
            categories = ["Pekerjaan", "Belajar", "Pribadi", "Kebiasaan"]
            category_breakdown = {}
            for cat in categories:
                cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE category = ?", (cat,))
                cat_total = cursor.fetchone()["count"]
                cursor.execute(
                    "SELECT COUNT(*) as count FROM tasks WHERE category = ? AND is_completed = 1",
                    (cat,),
                )
                cat_done = cursor.fetchone()["count"]
                category_breakdown[cat] = {
                    "total": cat_total,
                    "completed": cat_done,
                    "rate": (cat_done / cat_total) if cat_total > 0 else 0.0,
                }

            # Statistik Pomodoro Hari Ini
            cursor.execute(
                """
                SELECT COUNT(*) as total_sessions, COALESCE(SUM(duration_minutes), 0) as total_minutes
                FROM pomodoro_sessions
                WHERE completed_at LIKE ? AND session_type = 'Fokus'
                """,
                (f"{today_prefix}%",),
            )
            pomo_data = cursor.fetchone()
            pomo_sessions = pomo_data["total_sessions"]
            focus_minutes = pomo_data["total_minutes"]

            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "completion_rate": completion_rate,
                "category_breakdown": category_breakdown,
                "today_sessions": pomo_sessions,
                "today_focus_minutes": focus_minutes,
            }
        finally:
            conn.close()
