"""
main.py
Entry Point Aplikasi Mobile Produktivitas: FocusPulse (To-Do, Habit Tracker, & Pomodoro).
Dikembangkan menggunakan Python dan framework modern Flet (Flutter-based).
"""

import flet as ft
from database import DatabaseManager
from views import DashboardView, TasksView, PomodoroView


def main(page: ft.Page):
    # 1. Konfigurasi Halaman & Tema Mobile Modern
    page.title = "FocusPulse - Productivity Mobile App"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.padding = 0

    # Simulasi layar smartphone jika dijalankan di Desktop
    try:
        page.overlay.append(
            ft.Window(
                width=420,
                height=820,
                resizable=False,
                maximizable=False,
                center=True,
            )
        )
    except Exception:
        pass

    # 2. Inisialisasi Database Lokal SQLite
    db = DatabaseManager()

    # 3. Deklarasi Handler Navigasi & Sinkronisasi Antar Tab
    def navigate_to_tab(index: int):
        switch_view(index)

    def on_tasks_changed():
        dashboard_view.refresh()

    def on_pomodoro_completed():
        dashboard_view.refresh()
        pomodoro_view.refresh_stats()

    # 4. Inisialisasi Tampilan (Views)
    dashboard_view = DashboardView(db, on_navigate_tab=navigate_to_tab)
    tasks_view = TasksView(db, on_data_changed=on_tasks_changed)
    pomodoro_view = PomodoroView(db, on_session_completed=on_pomodoro_completed)

    views = [dashboard_view, tasks_view, pomodoro_view]
    tasks_view.visible = False
    pomodoro_view.visible = False

    def switch_view(index: int):
        nav_bar.selected_index = index
        for i, v in enumerate(views):
            v.visible = (i == index)
        if index == 0:
            dashboard_view.refresh()
        elif index == 1:
            tasks_view.refresh()
        elif index == 2:
            pomodoro_view.refresh_stats()
        page.update()

    # 5. Mobile Bottom Navigation Bar
    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=lambda e: switch_view(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.CHECK_CIRCLE,
                label="Tugas & Habit",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.TIMER_OUTLINED,
                selected_icon=ft.Icons.TIMER,
                label="Pomodoro",
            ),
        ],
    )
    page.navigation_bar = nav_bar

    # 6. Wadah Responsif Mobile (Smartphone Aspect Ratio)
    root_container = ft.Container(
        alignment=ft.Alignment(0, 0),
        expand=True,
        content=ft.Container(
            width=450,
            expand=True,
            content=ft.Stack(
                expand=True,
                controls=views,
            ),
        ),
    )

    page.add(root_container)


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
