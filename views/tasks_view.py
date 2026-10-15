"""
views/tasks_view.py
Tampilan Pengelolaan To-Do List & Habit Tracker.
Mendukung penambahan tugas, penandaan selesai (toggle), penghapusan, dan filter per kategori.
"""

from typing import Callable, Optional
import flet as ft
from database import DatabaseManager
from models import Task
from utils import get_page, safe_update, show_dialog_safe, close_dialog_safe, show_snack_safe


class TasksView(ft.Container):
    """Komponen Kelola Tugas & Kebiasaan."""

    CATEGORIES = ["Semua", "Pekerjaan", "Belajar", "Pribadi", "Kebiasaan"]
    CATEGORY_COLORS = {
        "Pekerjaan": ft.Colors.BLUE,
        "Belajar": ft.Colors.PURPLE,
        "Pribadi": ft.Colors.GREEN,
        "Kebiasaan": ft.Colors.ORANGE,
    }

    def __init__(self, db: DatabaseManager, on_data_changed: Optional[Callable[[], None]] = None):
        super().__init__()
        self.db = db
        self.on_data_changed = on_data_changed
        self.expand = True
        self.padding = 16

        self.current_category = "Semua"
        self.tasks_list_column = ft.Column(spacing=10)

        # Dialog Tambah Tugas
        self.new_task_input = ft.TextField(
            label="Nama Tugas / Kebiasaan",
            hint_text="Misal: Selesaikan laporan sprint...",
            autofocus=True,
            border_radius=10,
        )
        self.category_dropdown = ft.Dropdown(
            label="Kategori",
            value="Pekerjaan",
            options=[
                ft.dropdown.Option("Pekerjaan"),
                ft.dropdown.Option("Belajar"),
                ft.dropdown.Option("Pribadi"),
                ft.dropdown.Option("Kebiasaan"),
            ],
            border_radius=10,
        )
        self.add_dialog = self._create_add_dialog()

        self.content = self._build_layout()
        self.refresh()

    def _build_layout(self) -> ft.Control:
        """Menyusun layout utama tab Tugas."""
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Tugas & Habits", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("Atur prioritas dan bangun rutinitas positif", size=13, color=ft.Colors.GREY_400),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE,
                    icon_color=ft.Colors.PRIMARY,
                    icon_size=36,
                    tooltip="Tambah Tugas Baru",
                    on_click=self._open_add_dialog,
                ),
            ],
        )

        # Filter Chips Bar (Horizontal Scroll)
        self.chips_row = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=[self._create_filter_chip(cat) for cat in self.CATEGORIES],
        )

        return ft.Column(
            expand=True,
            spacing=14,
            controls=[
                header,
                self.chips_row,
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                ft.ListView(
                    expand=True,
                    spacing=10,
                    controls=[self.tasks_list_column],
                ),
            ],
        )

    def _create_filter_chip(self, category_name: str) -> ft.Chip:
        """Membuat chip filter kategori."""
        is_selected = self.current_category == category_name
        return ft.Chip(
            label=ft.Text(category_name),
            selected=is_selected,
            on_select=lambda e, cat=category_name: self._select_category(cat),
        )

    def _select_category(self, category_name: str):
        """Memilih kategori filter dan memperbarui daftar tugas."""
        self.current_category = category_name
        for chip in self.chips_row.controls:
            chip.selected = chip.label.value == category_name
        safe_update(self.chips_row)
        self.refresh()

    def _create_add_dialog(self) -> ft.AlertDialog:
        """Membuat modal dialog penambahan tugas."""
        return ft.AlertDialog(
            title=ft.Text("Tambah Tugas / Habit Baru", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    self.new_task_input,
                    self.category_dropdown,
                ],
            ),
            actions=[
                ft.TextButton("Batal", on_click=self._close_add_dialog),
                ft.FilledButton("Simpan", on_click=self._save_new_task),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _open_add_dialog(self, _=None):
        """Membuka dialog tambah tugas secara cross-version."""
        self.new_task_input.value = ""
        self.new_task_input.error_text = None
        pg = get_page(self)
        if pg:
            show_dialog_safe(pg, self.add_dialog)

    def _close_add_dialog(self, _=None):
        """Menutup dialog tambah tugas secara cross-version."""
        pg = get_page(self)
        if pg:
            close_dialog_safe(pg, self.add_dialog)

    def _save_new_task(self, _=None):
        """Validasi dan simpan tugas baru ke database."""
        title = self.new_task_input.value.strip() if self.new_task_input.value else ""
        if not title:
            self.new_task_input.error_text = "Judul tugas tidak boleh kosong!"
            safe_update(self.new_task_input)
            return

        cat = self.category_dropdown.value or "Pekerjaan"
        self.db.add_task(title=title, category=cat)
        self._close_add_dialog()

        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()

        pg = get_page(self)
        if pg:
            show_snack_safe(pg, "Tugas baru berhasil ditambahkan!")

    def _create_task_item(self, task: Task) -> ft.Control:
        """Membuat komponen kartu tugas individual."""
        cat_color = self.CATEGORY_COLORS.get(task.category, ft.Colors.PRIMARY)

        title_style = ft.TextStyle(
            decoration=ft.TextDecoration.LINE_THROUGH if task.is_completed else ft.TextDecoration.NONE,
            color=ft.Colors.GREY_400 if task.is_completed else None,
            weight=ft.FontWeight.W_500,
            size=15,
        )

        return ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH if not task.is_completed else ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=12,
            padding=ft.Padding(12, 8, 12, 8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Checkbox(
                                value=task.is_completed,
                                on_change=lambda e, t_id=task.id: self._toggle_task(t_id),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=4,
                                controls=[
                                    ft.Text(task.title, style=title_style, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Container(
                                        bgcolor=ft.Colors.with_opacity(0.15, cat_color),
                                        padding=ft.Padding(8, 2, 8, 2),
                                        border_radius=6,
                                        content=ft.Text(
                                            task.category,
                                            size=10,
                                            color=cat_color,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        icon_size=20,
                        tooltip="Hapus Tugas",
                        on_click=lambda e, t_id=task.id: self._delete_task(t_id),
                    ),
                ],
            ),
        )

    def _toggle_task(self, task_id: int):
        """Mengubah status tugas dan memicu sinkronisasi data."""
        self.db.toggle_task(task_id)
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()

    def _delete_task(self, task_id: int):
        """Menghapus tugas dari database."""
        self.db.delete_task(task_id)
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()
        pg = get_page(self)
        if pg:
            show_snack_safe(pg, "Tugas telah dihapus.")

    def refresh(self):
        """Memuat ulang daftar tugas sesuai filter kategori."""
        tasks = self.db.get_tasks(category=self.current_category)
        self.tasks_list_column.controls.clear()

        if not tasks:
            empty_state = ft.Container(
                alignment=ft.Alignment(0, 0),
                padding=32,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=56, color=ft.Colors.GREY_500),
                        ft.Text("Tidak ada tugas di kategori ini", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_400),
                        ft.Text("Tekan tombol + di kanan atas untuk menambahkan", size=12, color=ft.Colors.GREY_500),
                    ],
                ),
            )
            self.tasks_list_column.controls.append(empty_state)
        else:
            for task in tasks:
                self.tasks_list_column.controls.append(self._create_task_item(task))

        safe_update(self.tasks_list_column)
