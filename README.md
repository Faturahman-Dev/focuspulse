# 🚀 FocusPulse - Mobile Productivity & Habit Tracker

Aplikasi mobile tracking produktivitas cross-platform (Android, iOS, Desktop, Web) yang dibangun menggunakan **Python** dan framework **Flet** (berbasis engine Flutter). Aplikasi ini menggabungkan pengelolaan tugas & habit, pencatat waktu fokus Pomodoro, dan dashboard statistik real-time dengan penyimpanan database lokal SQLite.

---

## 📱 Fitur Utama

1. **Task & Habit Tracker:**
   - Tambah, tandai selesai (*toggle check*), dan hapus tugas harian.
   - Filter cepat berdasarkan kategori: **Pekerjaan**, **Belajar**, **Pribadi**, dan **Kebiasaan (Habit)**.
   - Efek visual *strike-through* dan penanda warna kategori yang dinamis.

2. **Timer Pomodoro & Fokus Terarah:**
   - 3 Mode: **Fokus (25m)**, **Istirahat Pendek (5m)**, dan **Istirahat Panjang (15m)**.
   - Animasi hitung mundur melingkar (*Circular Progress Ring*) yang responsif.
   - Kontrol **Mulai / Jeda / Reset**.
   - Berjalan di *background thread* tanpa membuat antarmuka (UI) membeku.
   - Pencatatan riwayat sesi fokus otomatis ke database saat waktu habis.

3. **Dashboard Ringkasan Produktivitas:**
   - *Progress Bar* persentase penyelesaian tugas harian.
   - Metrik ringkas: Total Tugas, Selesai, Menunggu, dan Total Menit Fokus.
   - *Breakdown* capaian per kategori dengan progress bar individual.
   - Pesan motivasi harian berdasarkan tingkat penyelesaian.

4. **Penyimpanan Lokal (Local Storage):**
   - Menggunakan database **SQLite** (`productivity.db`), data aman dan tetap tersimpan meski aplikasi ditutup.
   - Dilengkapi *seeding data* otomatis saat pertama kali dijalankan.

---

## 📂 Struktur Direktori Proyek

```text
FocusPulse/
│
├── main.py                 # Entry point aplikasi & konfigurasi frame mobile
├── database.py             # SQLite Database Manager & fungsi CRUD
├── models.py               # Data class untuk Task dan PomodoroSession
├── utils.py                # Helper dialog, snackbar, dan kompatibilitas versi Flet
│
├── views/                  # Modul antarmuka pengguna (UI Views)
│   ├── __init__.py         # Inisialisasi package views
│   ├── dashboard_view.py   # Halaman Dashboard ringkasan produktivitas
│   ├── tasks_view.py       # Halaman pengelolaan To-Do List & Habit Tracker
│   └── pomodoro_view.py    # Halaman Timer Pomodoro & Kontrol Fokus
│
├── requirements.txt        # Daftar pustaka / dependensi Python
└── README.md               # Dokumentasi lengkap & panduan build mobile
```

---

## 🛠️ Panduan Instalasi & Menjalankan

### 1. Prasyarat
- Python 3.9 atau yang lebih baru telah terpasang.

### 2. Instalasi Dependensi
Buka terminal / PowerShell di direktori proyek, lalu jalankan:

```bash
pip install -r requirements.txt
```

*(Atau cukup `pip install flet`)*

### 3. Menjalankan Aplikasi di Komputer (Mode Preview Mobile)
Jalankan perintah berikut:

```bash
python main.py
```
Aplikasi akan langsung terbuka dalam jendela berukuran proporsional layar smartphone (420 x 820 px).

---

## 📲 Panduan Menjalankan & Build ke Android / iOS

Flet menggunakan Flutter sebagai runtime visualnya, sehingga sangat mudah untuk diuji dan dikompilasi ke mobile native:

### Opsi A: Uji Coba Cepat di HP Fisik (Tanpa Perlu Build APK)
1. Unduh aplikasi **Flet** resmi dari **Google Play Store** (Android) atau **App Store** (iOS).
2. Di komputer Anda, jalankan:
   ```bash
   flet run --mobile
   ```
3. Scan **QR code** yang muncul di terminal menggunakan aplikasi Flet di smartphone Anda. Aplikasi akan langsung berjalan di HP Anda dengan *hot-reload*!

---

### Opsi B: Build Standalone APK (Android)
Untuk menghasilkan file installer `.apk` mandiri yang siap diinstal:

1. Pastikan Anda telah memasang Flutter SDK atau gunakan Flet Build Tool:
   ```bash
   pip install flet-cli
   ```
2. Jalankan perintah build:
   ```bash
   flet build apk
   ```
   File APK siap pakai akan tersedia di folder `build/apk/`.

### Opsi C: Build untuk iOS (macOS)
Bagi pengguna macOS dengan Xcode terpasang:
```bash
flet build ipa
```

---

## 💡 Mengapa Memilih Flet Dibanding Framework Lain?

- **Dibandingkan Kivy:** Kivy menggunakan styling non-standar dan membutuhkan setup compiler C/Cython yang berat untuk build ke Android. Sebaliknya, **Flet** merender widget native Flutter dengan Material Design 3, performa 60–120 FPS, responsif, dan didukung ekosistem Flutter modern.
- **Python Murni:** Semua logika bisnis, manipulasi database, dan pembuatan tampilan ditulis 100% menggunakan Python yang bersih dan modular.
