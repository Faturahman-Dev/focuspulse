"""
views/pomodoro_view.py
Tampilan Timer Pomodoro & Pencatat Waktu Fokus Sederhana.
Mendukung mode Fokus (25m), Istirahat Pendek (5m), dan Istirahat Panjang (15m)
dengan kontrol Start, Pause, Reset, serta pencatatan otomatis ke database lokal.
"""

import threading
import time
from typing import Callable, Optional
import flet as ft
from database import DatabaseManager
from utils import get_page, safe_update, show_snack_safe


class PomodoroView(ft.Container):
    """Komponen Timer Pomodoro Cross-Platform."""

    MODES = {
        "Fokus": {
            "name": "Fokus",
            "duration": 25 * 60,
            "label": "🎯 Fokus (25m)",
            "color": ft.Colors.PRIMARY,
            "desc": "Singkirkan distraksi dan fokus penuh pada satu tugas.",
        },
        "Istirahat Pendek": {
            "name": "Istirahat Pendek",
            "duration": 5 * 60,
            "label": "☕ Santai (5m)",
            "color": ft.Colors.GREEN,
            "desc": "Tarik nafas, minum air, atau lakukan peregangan ringan.",
        },
        "Istirahat Panjang": {
            "name": "Istirahat Panjang",
            "duration": 15 * 60,
            "label": "🌴 Rehat (15m)",
            "color": ft.Colors.TEAL,
            "desc": "Waktu istirahat lebih lama untuk memulihkan energi mentalmu.",
        },
    }

    def __init__(self, db: DatabaseManager, on_session_completed: Optional[Callable[[], None]] = None):
        super().__init__()
        self.db = db
        self.on_session_completed = on_session_completed
        self.expand = True
        self.padding = 16

        self.current_mode = "Fokus"
        self.total_seconds = self.MODES["Fokus"]["duration"]
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self._timer_thread: Optional[threading.Thread] = None

        # UI Controls
        self.timer_text = ft.Text("25:00", size=46, weight=ft.FontWeight.BOLD)
        self.mode_badge_text = ft.Text("SESI FOKUS", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
        self.desc_text = ft.Text(self.MODES["Fokus"]["desc"], size=13, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)

        self.progress_ring = ft.ProgressRing(
            value=1.0,
            stroke_width=12,
            width=230,
            height=230,
            color=ft.Colors.PRIMARY,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

        self.toggle_btn = ft.FilledButton(
            "Mulai Fokus",
            icon=ft.Icons.PLAY_ARROW,
            height=48,
            width=160,
            on_click=self._toggle_timer,
        )

        self.reset_btn = ft.OutlinedButton(
            "Reset",
            icon=ft.Icons.REPLAY,
            height=48,
            width=120,
            on_click=self._reset_timer,
        )

        self.session_summary_text = ft.Text("Hari ini: 0 sesi selesai (0 menit)", size=13, color=ft.Colors.GREY_400)

        self.content = self._build_layout()
        self.refresh_stats()

    def _build_layout(self) -> ft.Control:
        """Menyusun layout visual Timer Pomodoro."""
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Timer Fokus & Pomodoro", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Tingkatkan produktivitas dengan interval fokus terarah", size=13, color=ft.Colors.GREY_400),
            ],
        )

        # Mode Chips (Horizontal selector)
        self.mode_chips_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                self._create_mode_chip("Fokus"),
                self._create_mode_chip("Istirahat Pendek"),
                self._create_mode_chip("Istirahat Panjang"),
            ],
        )

        # Circular Timer Display menggunakan Stack
        timer_center = ft.Container(
            alignment=ft.Alignment(0, 0),
            width=230,
            height=230,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    self.timer_text,
                    self.mode_badge_text,
                ],
            ),
        )

        timer_display = ft.Container(
            alignment=ft.Alignment(0, 0),
            padding=20,
            content=ft.Stack(
                alignment=ft.Alignment(0, 0),
                controls=[
                    self.progress_ring,
                    timer_center,
                ],
            ),
        )

        # Control Buttons
        actions_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=14,
            controls=[
                self.toggle_btn,
                self.reset_btn,
            ],
        )

        # Bottom Tip & Today's Metric Card
        tip_card = ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=14,
            padding=14,
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=ft.Colors.AMBER_400, size=24),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text("Pencapaian Fokus Hari Ini", size=13, weight=ft.FontWeight.W_600),
                            self.session_summary_text,
                        ],
                    ),
                ],
            ),
        )

        return ft.ListView(
            expand=True,
            spacing=16,
            controls=[
                header,
                self.mode_chips_row,
                timer_display,
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    content=self.desc_text,
                ),
                actions_row,
                tip_card,
            ],
        )

    def _create_mode_chip(self, mode_key: str) -> ft.Chip:
        """Membuat chip pilihan mode Pomodoro."""
        mode_info = self.MODES[mode_key]
        return ft.Chip(
            label=ft.Text(mode_info["label"]),
            selected=(self.current_mode == mode_key),
            on_select=lambda e, m=mode_key: self._switch_mode(m),
        )

    def _switch_mode(self, mode_key: str):
        """Beralih mode pomodoro dan mereset waktu timer."""
        if self.is_running:
            self._stop_timer()

        self.current_mode = mode_key
        mode_info = self.MODES[mode_key]
        self.total_seconds = mode_info["duration"]
        self.remaining_seconds = self.total_seconds

        # Update styling sesuai mode
        self.progress_ring.color = mode_info["color"]
        self.progress_ring.value = 1.0
        self.mode_badge_text.value = f"SESI {mode_info['name'].upper()}"
        self.mode_badge_text.color = mode_info["color"]
        self.desc_text.value = mode_info["desc"]

        # Update status chip
        for chip in self.mode_chips_row.controls:
            chip.selected = (chip.label.value == mode_info["label"])

        self._update_display()

    def _format_time(self, seconds: int) -> str:
        """Format detik menjadi format MM:SS."""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def _update_display(self):
        """Memperbarui teks waktu dan progress ring."""
        self.timer_text.value = self._format_time(self.remaining_seconds)
        self.progress_ring.value = (self.remaining_seconds / self.total_seconds) if self.total_seconds > 0 else 0.0
        safe_update(self.timer_text)
        safe_update(self.progress_ring)

    def _toggle_timer(self, _=None):
        """Memulai atau menjeda timer fokus."""
        if self.is_running:
            self._stop_timer()
        else:
            self._start_timer()

    def _start_timer(self):
        """Memulai hitungan mundur timer dalam thread latar belakang."""
        self.is_running = True
        self.toggle_btn.content = "Jeda"
        self.toggle_btn.icon = ft.Icons.PAUSE
        safe_update(self.toggle_btn)

        self._timer_thread = threading.Thread(target=self._run_timer_loop, daemon=True)
        self._timer_thread.start()

    def _stop_timer(self):
        """Menjeda timer."""
        self.is_running = False
        self.toggle_btn.content = "Lanjutkan"
        self.toggle_btn.icon = ft.Icons.PLAY_ARROW
        safe_update(self.toggle_btn)

    def _reset_timer(self, _=None):
        """Mereset timer kembali ke durasi penuh mode aktif."""
        self.is_running = False
        self.remaining_seconds = self.total_seconds
        self.toggle_btn.content = f"Mulai {self.current_mode}"
        self.toggle_btn.icon = ft.Icons.PLAY_ARROW
        safe_update(self.toggle_btn)
        self._update_display()

    def _run_timer_loop(self):
        """Loop eksekusi timer di latar belakang."""
        while self.is_running and self.remaining_seconds > 0:
            time.sleep(1)
            if not self.is_running:
                break
            self.remaining_seconds -= 1
            self._update_display()

        if self.remaining_seconds <= 0 and self.is_running:
            self.is_running = False
            self._on_timer_complete()

    def _on_timer_complete(self):
        """Dipanggil saat waktu timer habis."""
        duration_mins = self.total_seconds // 60

        # Simpan sesi ke database jika mode Fokus
        if self.current_mode == "Fokus":
            self.db.add_pomodoro_session("Fokus", duration_mins)
            msg = f"🎉 Luar biasa! Sesi fokus {duration_mins} menit telah selesai!"
        else:
            self.db.add_pomodoro_session(self.current_mode, duration_mins)
            msg = f"☕ Waktu istirahat selesai! Siap kembali fokus?"

        self.toggle_btn.content = "Mulai Baru"
        self.toggle_btn.icon = ft.Icons.PLAY_ARROW
        safe_update(self.toggle_btn)

        pg = get_page(self)
        if pg:
            show_snack_safe(pg, msg, duration_ms=4000)

        self.refresh_stats()

        if self.on_session_completed:
            self.on_session_completed()

    def refresh_stats(self):
        """Memperbarui ringkasan sesi Pomodoro hari ini."""
        sessions = self.db.get_today_pomodoro_sessions()
        focus_sessions = [s for s in sessions if s.session_type == "Fokus"]
        total_mins = sum(s.duration_minutes for s in focus_sessions)
        self.session_summary_text.value = f"Hari ini: {len(focus_sessions)} sesi selesai ({total_mins} menit fokus)"
        safe_update(self.session_summary_text)
