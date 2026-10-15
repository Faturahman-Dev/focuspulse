"""
models.py
Definisi Data Model untuk Task, Habit, dan Pomodoro Session.
Menggunakan dataclass untuk representasi data yang bersih dan tipe yang jelas.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """Model untuk Tugas dan Kebiasaan harian."""
    id: int
    title: str
    category: str  # 'Pekerjaan', 'Belajar', 'Pribadi', 'Kebiasaan'
    is_completed: bool
    created_at: str
    completed_at: Optional[str] = None


@dataclass
class PomodoroSession:
    """Model untuk Riwayat Sesi Pomodoro yang diselesaikan."""
    id: int
    session_type: str  # 'Fokus', 'Istirahat Pendek', 'Istirahat Panjang'
    duration_minutes: int
    completed_at: str
