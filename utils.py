"""
utils.py
Helper fungsi umum untuk kompatibilitas lintas versi Flet (0.x - 1.x)
serta penanganan UI & Dialog yang aman dari exception saat unmounted.
"""

from typing import Optional
import flet as ft


def get_page(control: ft.Control) -> Optional[ft.Page]:
    """Mendapatkan referensi ft.Page secara aman tanpa melempar RuntimeError jika belum di-mount."""
    try:
        return control.page
    except RuntimeError:
        return None


def safe_update(control: ft.Control):
    """Memperbarui UI control hanya jika sudah terhubung ke Page."""
    try:
        control.update()
    except RuntimeError:
        pass


def show_dialog_safe(page: ft.Page, dialog: ft.AlertDialog):
    """Menampilkan modal dialog secara kompatibel di semua versi Flet."""
    if hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
    elif hasattr(page, "open"):
        page.open(dialog)
    else:
        page.dialog = dialog
        dialog.open = True
        page.update()


def close_dialog_safe(page: ft.Page, dialog: ft.AlertDialog):
    """Menutup modal dialog secara kompatibel di semua versi Flet."""
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    elif hasattr(page, "close"):
        page.close(dialog)
    else:
        dialog.open = False
        page.update()


def show_snack_safe(page: ft.Page, message: str, duration_ms: int = 2500):
    """Menampilkan notifikasi SnackBar mengambang."""
    sb = ft.SnackBar(
        content=ft.Text(message, size=14, weight=ft.FontWeight.W_500),
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=duration_ms,
    )
    if hasattr(page, "show_dialog"):
        page.show_dialog(sb)
    elif hasattr(page, "open"):
        page.open(sb)
    else:
        page.snack_bar = sb
        sb.open = True
        page.update()
