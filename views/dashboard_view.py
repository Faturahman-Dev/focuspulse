"""
views/dashboard_view.py
Tampilan Dashboard Ringkasan Produktivitas.
Menampilkan progres harian, statistik penyelesaian tugas, breakdown kategori, dan sesi Pomodoro.
"""

from datetime import datetime
from typing import Callable, Optional
import flet as ft
from database import DatabaseManager
from utils import safe_update


class DashboardView(ft.Container):
    """Komponen Dashboard Produktivitas Harian."""

    def __init__(self, db: DatabaseManager, on_navigate_tab: Optional[Callable[[int], None]] = None):
        super().__init__()
        self.db = db
        self.on_navigate_tab = on_navigate_tab
        self.expand = True
        self.padding = 16

        # Dynamic controls yang akan diupdate saat refresh
        self.progress_bar = ft.ProgressBar(value=0.0, height=10, border_radius=5, color=ft.Colors.PRIMARY)
        self.progress_text = ft.Text("0%", size=20, weight=ft.FontWeight.BOLD)
        self.progress_subtitle = ft.Text("0 dari 0 tugas selesai", size=13, color=ft.Colors.GREY_400)
        self.motivation_text = ft.Text("", size=12, italic=True, color=ft.Colors.PRIMARY)

        # Stat counter cards
        self.total_card_val = ft.Text("0", size=22, weight=ft.FontWeight.BOLD)
        self.completed_card_val = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
        self.pending_card_val = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE)
        self.pomodoro_card_val = ft.Text("0 sesi (0m)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE)

        # Container untuk category breakdown
        self.categories_column = ft.Column(spacing=10)

        # Build UI layout
        self.content = self._build_layout()
        self.refresh()

    def _build_layout(self) -> ft.Control:
        """Menyusun seluruh elemen UI Dashboard."""
        today_str = datetime.now().strftime("%A, %d %B %Y")

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Halo, Pejuang Fokus! 👋", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(today_str, size=13, color=ft.Colors.GREY_400),
                    ],
                ),
                ft.CircleAvatar(
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.ON_PRIMARY_CONTAINER),
                    radius=22,
                ),
            ],
        )

        hero_card = ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=16,
            padding=18,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Target Produktivitas Hari Ini", size=15, weight=ft.FontWeight.W_600),
                            self.progress_text,
                        ],
                    ),
                    self.progress_bar,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.progress_subtitle,
                            self.motivation_text,
                        ],
                    ),
                ],
            ),
        )

        stats_grid = ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        self._create_stat_card("Total Tugas", self.total_card_val, ft.Icons.CHECKLIST, ft.Colors.BLUE_400),
                        self._create_stat_card("Selesai", self.completed_card_val, ft.Icons.TASK_ALT, ft.Colors.GREEN_400),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self._create_stat_card("Menunggu", self.pending_card_val, ft.Icons.PENDING_ACTIONS, ft.Colors.ORANGE_400),
                        self._create_stat_card("Fokus Pomodoro", self.pomodoro_card_val, ft.Icons.TIMER, ft.Colors.PURPLE_400),
                    ],
                ),
            ],
        )

        categories_section = ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=16,
            padding=16,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Progres per Kategori", size=15, weight=ft.FontWeight.W_600),
                            ft.Icon(ft.Icons.CATEGORY, size=18, color=ft.Colors.GREY_400),
                        ],
                    ),
                    self.categories_column,
                ],
            ),
        )

        quick_pomodoro_btn = ft.FilledButton(
            "Mulai Sesi Fokus Pomodoro ⏱️",
            icon=ft.Icons.PLAY_ARROW,
            height=50,
            on_click=lambda _: self.on_navigate_tab(2) if self.on_navigate_tab else None,
        )

        return ft.ListView(
            expand=True,
            spacing=18,
            controls=[
                header,
                hero_card,
                ft.Text("Ringkasan Metrik", size=16, weight=ft.FontWeight.BOLD),
                stats_grid,
                categories_section,
                quick_pomodoro_btn,
                ft.Container(height=20),
            ],
        )

    def _create_stat_card(self, title: str, val_control: ft.Text, icon: str, icon_color: str) -> ft.Control:
        """Helper untuk membuat kartu statistik ringkas."""
        return ft.Container(
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=14,
            padding=14,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(title, size=12, color=ft.Colors.GREY_400),
                            ft.Icon(icon, size=18, color=icon_color),
                        ],
                    ),
                    val_control,
                ],
            ),
        )

    def refresh(self):
        """Memperbarui seluruh data ringkasan dari database lokal."""
        summary = self.db.get_summary()

        total = summary["total_tasks"]
        completed = summary["completed_tasks"]
        pending = summary["pending_tasks"]
        rate = summary["completion_rate"]
        pomo_sessions = summary["today_sessions"]
        pomo_mins = summary["today_focus_minutes"]

        # Update hero progress
        self.progress_bar.value = rate
        percentage = int(rate * 100)
        self.progress_text.value = f"{percentage}%"
        self.progress_subtitle.value = f"{completed} dari {total} tugas selesai"

        if rate == 1.0 and total > 0:
            self.motivation_text.value = "🌟 Target Sempurna!"
        elif rate >= 0.7:
            self.motivation_text.value = "🔥 Luar biasa!"
        elif rate >= 0.4:
            self.motivation_text.value = "⚡ Terus pertahankan!"
        else:
            self.motivation_text.value = "🌱 Ayo mulai bertindak!"

        # Update stat cards
        self.total_card_val.value = str(total)
        self.completed_card_val.value = str(completed)
        self.pending_card_val.value = str(pending)
        self.pomodoro_card_val.value = f"{pomo_sessions} sesi ({pomo_mins}m)"

        # Update categories breakdown
        self.categories_column.controls.clear()
        category_colors = {
            "Pekerjaan": ft.Colors.BLUE,
            "Belajar": ft.Colors.PURPLE,
            "Pribadi": ft.Colors.GREEN,
            "Kebiasaan": ft.Colors.ORANGE,
        }

        for cat_name, cat_data in summary["category_breakdown"].items():
            cat_tot = cat_data["total"]
            cat_done = cat_data["completed"]
            cat_rate = cat_data["rate"]
            bar_color = category_colors.get(cat_name, ft.Colors.PRIMARY)

            cat_item = ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(cat_name, size=13, weight=ft.FontWeight.W_500),
                            ft.Text(f"{cat_done}/{cat_tot}", size=12, color=ft.Colors.GREY_400),
                        ],
                    ),
                    ft.ProgressBar(value=cat_rate, height=6, border_radius=3, color=bar_color),
                ],
            )
            self.categories_column.controls.append(cat_item)

        safe_update(self)
