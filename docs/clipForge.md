PROJECT: ClipForge

Buat aplikasi Android modern bernama ClipForge.

ClipForge adalah aplikasi AI Video Clipper yang memungkinkan pengguna memasukkan link YouTube lalu membuat clip video otomatis menggunakan AI.

Target utama:

- Android (Kotlin + Jetpack Compose)
- Backend (Python FastAPI)
- PostgreSQL
- Supabase Auth
- FFmpeg
- yt-dlp
- Whisper
- YOLOv8
- MediaPipe

Fokus pada arsitektur yang scalable, clean, dan siap dikembangkan menjadi produk komersial.

---

Fitur Utama

Import Video

User dapat:

- Paste URL YouTube
- Melihat thumbnail
- Melihat judul video
- Melihat durasi video

Backend mengambil metadata otomatis menggunakan yt-dlp.

---

Manual Clip

User dapat menentukan:

- Start Time
- End Time

Video dipotong menggunakan FFmpeg.

---

AI Highlight Detection

AI menganalisis:

- Audio
- Subtitle
- Perubahan scene
- Aktivitas visual

Kemudian menghasilkan:

- Highlight terbaik
- Beberapa highlight otomatis
- Highlight score

---

Speech Search

User dapat mencari bagian video berdasarkan kata tertentu.

Contoh:

- giveaway
- tutorial
- winner

Sistem:

- Generate transkrip menggunakan Whisper
- Cari kata
- Temukan timestamp
- Buat clip otomatis

---

Scene Detection

Deteksi perpindahan scene otomatis.

Output:

- Daftar scene
- Preview scene
- Export clip

---

Object Tracking

AI dapat mendeteksi:

- Person
- Car
- Motorcycle
- Cat
- Dog

Output:

- Timestamp objek muncul
- Auto clip

Gunakan YOLOv8.

---

Face Tracking

AI dapat:

- Mendeteksi wajah
- Melacak wajah selama video
- Membuat clip otomatis saat wajah muncul

---

Gesture Tracking

Tambahkan fitur AI Gesture Tracking.

AI dapat mendeteksi:

- Orang menunjuk
- Tangan terangkat
- Melambaikan tangan
- Jempol
- Tepuk tangan
- Menghadap kamera

Gunakan:

- MediaPipe
- YOLO Pose

Output:

- Timestamp gesture muncul
- Auto clip

Contoh:

00:02:15 Person pointing right

00:04:08 Hand raised

00:08:22 Thumbs up

---

Shorts Generator

AI membuat video vertikal otomatis.

Fitur:

- Auto crop 9:16
- Auto subtitle
- Auto center subject
- Auto zoom speaker

Output:

- TikTok
- Reels
- Shorts

---

AI Processing Mode

Saat pertama kali membuka aplikasi, tampilkan pilihan:

Local AI

Deskripsi:

Semua proses dilakukan di perangkat pengguna.

Kelebihan:

- Privasi lebih baik
- Tidak perlu upload video
- Tidak menggunakan kuota server

Kekurangan:

- Lebih lambat
- Membutuhkan RAM lebih besar
- Fitur AI berat mungkin lebih lambat

---

Server AI

Deskripsi:

Video diproses menggunakan server GPU.

Kelebihan:

- Jauh lebih cepat
- Mendukung video panjang
- Tracking lebih akurat
- Cocok untuk pemrosesan massal

Kekurangan:

- Membutuhkan internet
- Video diupload ke server
- Menggunakan kuota server

---

Authentication

Gunakan Supabase Auth.

Metode login:

- Google
- Email & Password

---

Subscription System

Free Plan

Batas:

- Maksimal 3 video per hari
- Maksimal durasi video 1 menit per video
- Maksimal output 720p

Fitur tersedia:

- Manual Clip
- Basic Highlight
- Scene Detection

Tidak tersedia:

- Face Tracking
- Object Tracking
- Gesture Tracking
- Shorts Generator Pro

Tambahkan watermark kecil pada hasil video.

Prioritas queue rendah.

---

Premium Plan

Fitur:

- Unlimited video
- Unlimited durasi
- Hingga 4K Export
- Object Tracking
- Face Tracking
- Gesture Tracking
- Shorts Generator
- Speech Search
- Batch Processing
- No Watermark

Prioritas queue tinggi.

---

Dashboard

Menu:

- Home
- Import Video
- AI Clips
- Projects
- Subscription
- Settings

---

Settings

Tambahkan:

- Ganti mode AI
- Pilih kualitas output
- Hapus cache
- Kelola akun
- Kelola langganan

---

Admin Panel

Admin dapat:

- Melihat user
- Mengelola subscription
- Mengelola paket
- Melihat statistik penggunaan
- Melihat job queue
- Melihat penggunaan AI

---

Backend

Gunakan:

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic

Buat:

- API lengkap
- Authentication
- Subscription system
- Queue system
- Rate limit
- Logging
- Error handling

---

Database

Buat schema lengkap untuk:

- Users
- Subscription
- Videos
- Clips
- AI Jobs
- Payments
- Usage Tracking

---

Output yang Saya Inginkan

Berikan:

1. Arsitektur lengkap
2. Struktur folder project lengkap
3. Database schema lengkap
4. UI/UX flow lengkap
5. API specification lengkap
6. Backend implementation lengkap
7. Android implementation lengkap
8. Admin panel implementation
9. Environment variables
10. Docker deployment
11. Langkah instalasi
12. Source code lengkap setiap file
13. Penjelasan alasan pemilihan teknologi
14. Roadmap pengembangan dari MVP hingga production