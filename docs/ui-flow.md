# ClipForge — UI/UX Flow

**Version:** 1.0.0
**Last Updated:** 2026-05-31
**Platform:** Android (Jetpack Compose / Material 3)

---

## Daftar Isi

1. [Screen List](#1-screen-list)
2. [Navigation Flow](#2-navigation-flow)
3. [User Journey Map](#3-user-journey-map)
4. [Free User Flow](#4-free-user-flow)
5. [Premium User Flow](#5-premium-user-flow)
6. [Error States](#6-error-states)
7. [Loading States](#7-loading-states)
8. [Wireframe — Setiap Screen](#8-wireframe--setiap-screen)

---

## 1. Screen List

### Auth Group
| ID | Screen | Deskripsi |
|---|---|---|
| A-01 | OnboardingScreen | Pilih AI Mode (Local vs Server) — hanya tampil saat first launch |
| A-02 | LoginScreen | Login Google / Email+Password |

### Main Group (Bottom Navigation)
| ID | Screen | Deskripsi |
|---|---|---|
| M-01 | HomeScreen | Dashboard utama: statistik, video terbaru, shortcut |
| M-02 | ImportVideoScreen | Paste YouTube URL → preview → pilih aksi |
| M-03 | AIClipsScreen | List semua clip & hasil AI |
| M-04 | ProjectsScreen | Riwayat video yang diimport |
| M-05 | SettingsScreen | Preferensi, akun, AI mode |

### Video & Clip Group
| ID | Screen | Deskripsi |
|---|---|---|
| V-01 | VideoMetadataPreviewScreen | Preview info video sebelum import (judul, durasi, thumbnail) |
| V-02 | ClipOptionsScreen | Pilih jenis aksi: Manual / AI Feature |
| V-03 | ManualClipScreen | Set start & end time secara manual |
| V-04 | ClipDetailScreen | Detail satu clip: player, metadata, tombol download |

### AI Feature Group
| ID | Screen | Deskripsi |
|---|---|---|
| F-01 | AIHighlightScreen | Konfigurasi + progress + hasil Highlight Detection |
| F-02 | SpeechSearchScreen | Input kata pencarian + hasil timestamp |
| F-03 | SceneDetectionScreen | Grid scene + export pilihan |
| F-04 | ObjectTrackingScreen | Pilih class objek + hasil deteksi [Premium] |
| F-05 | FaceTrackingScreen | Hasil deteksi wajah + timeline [Premium] |
| F-06 | GestureTrackingScreen | Pilih gesture + timeline event [Premium] |
| F-07 | ShortsGeneratorScreen | Konfigurasi + preview Shorts 9:16 [Premium] |

### Subscription Group
| ID | Screen | Deskripsi |
|---|---|---|
| S-01 | SubscriptionScreen | Perbandingan plan + tombol upgrade |
| S-02 | PaymentConfirmationScreen | Konfirmasi setelah Google Play Billing sukses |

### System / Dialog
| ID | Komponen | Deskripsi |
|---|---|---|
| D-01 | PremiumGateDialog | Muncul saat Free user coba akses fitur Premium |
| D-02 | DailyLimitDialog | Muncul saat Free user sudah habis kuota harian (3 video/hari) |
| D-03 | JobProgressBottomSheet | Progress bar job yang sedang berjalan |
| D-04 | DeleteConfirmDialog | Konfirmasi hapus video atau clip |
| D-05 | NotificationPanel | Panel notifikasi in-app (job selesai, subscription expiring) |

---

## 2. Navigation Flow

```
App Launch
    │
    ├── [First Launch?] YES
    │       │
    │       └─► A-01 OnboardingScreen
    │               │
    │               └─► A-02 LoginScreen
    │                       │
    │                       └─► M-01 HomeScreen (Main)
    │
    └── [First Launch?] NO
            │
            ├── [Token Valid?] YES ──► M-01 HomeScreen (Main)
            └── [Token Valid?] NO  ──► A-02 LoginScreen


════════════════════════════════════════════════
MAIN NAVIGATION (Bottom Nav Bar)
════════════════════════════════════════════════

M-01 Home ◄──────────────────────────────────────┐
  │                                               │
  ├── Tap "Import Video" ──────────────────► M-02 ImportVideoScreen
  │                                               │
  ├── Tap video card ──────────────────────► V-02 ClipOptionsScreen
  │                                               │
  └── Tap notification ────────────────────► D-05 NotificationPanel

M-02 ImportVideoScreen
  │
  ├── Paste URL + Tap "Preview"
  │       │
  │       └─► [API: GET /videos/{id}/metadata]
  │               │
  │               └─► V-01 VideoMetadataPreviewScreen
  │                       │
  │                       └─► Tap "Import & Pilih Aksi"
  │                               │
  │                               └─► [API: POST /videos/import]
  │                                       │
  │                                       └─► V-02 ClipOptionsScreen

M-03 AIClipsScreen
  │
  └── Tap clip card ──────────────────────► V-04 ClipDetailScreen

M-04 ProjectsScreen
  │
  └── Tap video card ──────────────────────► V-02 ClipOptionsScreen

M-05 SettingsScreen
  │
  └── Tap "Kelola Langganan" ──────────────► S-01 SubscriptionScreen


════════════════════════════════════════════════
CLIP OPTIONS FLOW
════════════════════════════════════════════════

V-02 ClipOptionsScreen
  │
  ├── [Manual Clip] ──────────────────────────► V-03 ManualClipScreen
  │                                                   │
  │                                                   └─► [API: POST /clips/manual]
  │                                                           │
  │                                                           └─► V-04 ClipDetailScreen
  │
  ├── [AI Highlight] ─────────────────────────► F-01 AIHighlightScreen
  │
  ├── [Scene Detection] ──────────────────────► F-03 SceneDetectionScreen
  │
  ├── [Speech Search] 🔒──────────────────────► D-01 PremiumGateDialog
  │   [jika premium]  ────────────────────────► F-02 SpeechSearchScreen
  │
  ├── [Object Tracking] 🔒────────────────────► D-01 PremiumGateDialog
  │   [jika premium]  ────────────────────────► F-04 ObjectTrackingScreen
  │
  ├── [Face Tracking] 🔒──────────────────────► D-01 PremiumGateDialog
  │   [jika premium]  ────────────────────────► F-05 FaceTrackingScreen
  │
  ├── [Gesture Tracking] 🔒───────────────────► D-01 PremiumGateDialog
  │   [jika premium]  ────────────────────────► F-06 GestureTrackingScreen
  │
  └── [Shorts Generator] 🔒───────────────────► D-01 PremiumGateDialog
      [jika premium]  ────────────────────────► F-07 ShortsGeneratorScreen


════════════════════════════════════════════════
AI JOB FLOW (berlaku untuk semua AI feature screen)
════════════════════════════════════════════════

AI Feature Screen
  │
  └── Tap "Mulai Analisis"
          │
          └─► [API: POST /jobs/{type}]
                  │
                  └─► D-03 JobProgressBottomSheet (polling setiap N detik)
                          │
                          ├── [status = processing] ──► Update progress bar
                          │
                          ├── [status = done] ────────► Tampilkan hasil di screen
                          │                              Push notification
                          │
                          └── [status = failed] ───────► Error state + tombol Retry


════════════════════════════════════════════════
SUBSCRIPTION FLOW
════════════════════════════════════════════════

D-01 PremiumGateDialog
  │
  └── Tap "Upgrade Sekarang" ─────────────────► S-01 SubscriptionScreen
          │
          └── Tap "Mulai Premium"
                  │
                  └─► Google Play Billing SDK
                          │
                          ├── [Sukses] ─────────────► [API: POST /subscriptions/verify]
                          │                                   │
                          │                                   └─► S-02 PaymentConfirmationScreen
                          │
                          └── [Gagal] ──────────────► Error state di SubscriptionScreen
```

---

## 3. User Journey Map

### Journey 1: New User — First Time Import & Clip

```
Step  Aksi User                    System                          Emosi
────  ─────────────────────────    ──────────────────────────────  ──────
  1   Install & buka app           Tampil OnboardingScreen         😐 Penasaran
  2   Pilih "Server AI"            Simpan ke DataStore             😊 Mudah
  3   Login via Google             Supabase Auth → JWT             😊 Cepat
  4   Lihat HomeScreen             Dashboard kosong (empty state)  😐 "Apa selanjutnya?"
  5   Tap "Import Video"           Buka ImportVideoScreen          😊 Jelas
  6   Paste YouTube URL            Tampil preview metadata         😃 "Oke ini yang saya mau"
  7   Tap "Import & Pilih Aksi"    Video mulai download (async)    😊
  8   Lihat ClipOptionsScreen      Pilihan aksi tersedia           😊
  9   Pilih "AI Highlight"         Buka AIHighlightScreen          😃 Excited
 10   Tap "Mulai Analisis"         Job di-queue, progress tampil   😐 Menunggu
 11   Tunggu 1-3 menit             Progress bar update             😐 Sabar
 12   Hasil highlight tampil       5 momen terbaik dengan score    😄 Wow
 13   Tap clip → download          ClipDetailScreen → unduh MP4   😄 Puas
```

### Journey 2: Free User — Mentok Kuota

```
Step  Aksi User                    System                          Emosi
────  ─────────────────────────    ──────────────────────────────  ──────
  1   Import video ke-4 hari ini   [API: DAILY_LIMIT error]        😤 Frustrasi
  2   Muncul DailyLimitDialog      "3/3 video hari ini"            😤
  3   Tap "Upgrade Premium"        Buka SubscriptionScreen         😐 Mempertimbangkan
  4   Lihat fitur Premium          Tabel perbandingan              😊 Tertarik
  5   Tap "Mulai Premium"          Google Play Billing             😊
  6   Bayar berhasil               Subscription verified           😄 Lega
  7   Langsung bisa import lagi    Kuota unlimited                 😄 Senang
```

### Journey 3: Free User — Coba Fitur Premium

```
Step  Aksi User                    System                          Emosi
────  ─────────────────────────    ──────────────────────────────  ──────
  1   Di ClipOptionsScreen         Lihat "Gesture Tracking 🔒"     😐 Penasaran
  2   Tap "Gesture Tracking"       Muncul PremiumGateDialog        😐 Terhenti
  3   Baca daftar fitur Premium    Daftar keuntungan tampil        😊 Tertarik
  4   Tap "Nanti"                  Dialog tutup                    😐 Belum siap
  5   Coba "AI Highlight" (Free)   Berhasil diakses                😊 OK dulu ini
```

### Journey 4: Premium User — Full Workflow

```
Step  Aksi User                    System                          Emosi
────  ─────────────────────────    ──────────────────────────────  ──────
  1   Import video panjang 1 jam   Download mulai (server)         😊
  2   Pilih "Gesture Tracking"     Pilih gesture yang mau dicari   😊
  3   Centang thumbs_up, wave      Konfigurasi siap                😊
  4   Tap "Mulai Analisis"         Job priority 1 (premium)        😊 Lebih cepat
  5   Tunggu ±2 menit              Progress update tiap 3 detik    😊
  6   Lihat timeline hasil          8 gesture event tampil         😄 Bagus
  7   Tap event → preview clip     Mini player jalan               😄
  8   "Export Semua"               Batch clip di-generate          😄
  9   Download 8 clip sekaligus    ZIP download / satu per satu    😄 Produktif
 10   Pilih clip → Shorts          Buka ShortsGeneratorScreen      😊
 11   Auto-subtitle + 9:16 crop    Job Shorts running              😊
 12   Shorts siap, download        MP4 vertikal siap post          😄 Done
```

---

## 4. Free User Flow

### Batasan Free Plan
- Maks 3 video/hari
- Durasi video maks 60 detik
- Output maks 720p
- Watermark di semua clip
- Fitur: Manual Clip, AI Highlight, Scene Detection
- Queue priority rendah (antrian lebih lama)

### Free User — Diagram Lengkap

```
╔══════════════════════════════════════════════════════════╗
║                    FREE USER FLOW                        ║
╚══════════════════════════════════════════════════════════╝

Buka App
    │
    ▼
HomeScreen
    │
    ├── Banner: "3 video tersisa hari ini" (quota indicator)
    │
    └── Tap "Import Video"
            │
            ├── [Sudah 3 video hari ini?]
            │       YES ─────────────────────────────────────────────────┐
            │                                                            │
            │       NO                                                   │
            │       │                                                    │
            ▼       ▼                                                    ▼
      Paste URL            ┌───────────────────────────────────┐  D-02 DailyLimitDialog
            │              │ ⚠ Batas Harian Tercapai           │  ┌─────────────────────────┐
            ▼              │                                   │  │  🔒 Batas Harian         │
      [Preview Metadata]   │ Kamu sudah import 3 video hari   │  │                          │
            │              │ ini. Kembali besok atau upgrade  │  │  3/3 video hari ini.     │
            │              │ ke Premium untuk unlimited.      │  │  Reset pukul 00:00       │
            │              │                                   │  │                          │
            │              │ [Upgrade Premium]  [Tutup]        │  │  [Upgrade Premium]       │
            │              └───────────────────────────────────┘  │  [Balik Besok]           │
            │                                                       └─────────────────────────┘
            ▼
      [Durasi > 60 detik?]
            │
            YES ──► Toast: "Free plan hanya untuk video max 60 detik"
            │       Sub-teks: "Upgrade untuk video tanpa batas"
            │
            NO
            │
            ▼
      VideoMetadataPreviewScreen
            │
            └─► Tap "Import & Pilih Aksi"
                    │
                    ▼
              ClipOptionsScreen (Free View)
                    │
                    ├── [✅ TERSEDIA] Manual Clip
                    ├── [✅ TERSEDIA] AI Highlight
                    ├── [✅ TERSEDIA] Scene Detection
                    │
                    ├── [🔒 PREMIUM] Speech Search
                    ├── [🔒 PREMIUM] Object Tracking
                    ├── [🔒 PREMIUM] Face Tracking
                    ├── [🔒 PREMIUM] Gesture Tracking
                    └── [🔒 PREMIUM] Shorts Generator
                                        │
                                        └── Tap item 🔒
                                                │
                                                ▼
                                          D-01 PremiumGateDialog
                                          ┌─────────────────────────────────┐
                                          │  ⭐ Fitur Premium                │
                                          │                                 │
                                          │  [Nama Fitur] tersedia di       │
                                          │  ClipForge Premium.             │
                                          │                                 │
                                          │  ✓ Video unlimited              │
                                          │  ✓ Face & Gesture Tracking      │
                                          │  ✓ Export 4K                    │
                                          │  ✓ No Watermark                 │
                                          │  ✓ Speech Search & Shorts       │
                                          │                                 │
                                          │  [Upgrade Sekarang] [Nanti]     │
                                          └─────────────────────────────────┘


MANUAL CLIP (Free) ─────────────────────────────────────────────────────
    │
    ▼
ManualClipScreen
    │
    ├── Start Time: [00:00:12]
    ├── End Time:   [00:00:45]
    ├── Judul:      [input field]
    └── Tap "Buat Clip"
            │
            ▼
      [API: POST /clips/manual]
            │
            ▼
      Processing... (loading state)
            │
            ▼
      ClipDetailScreen
            │
            ├── Preview clip (ada watermark ClipForge)
            ├── Label: "⚠ Watermark aktif — Upgrade untuk hapus"
            └── [Download] [Hapus]


AI HIGHLIGHT (Free) ────────────────────────────────────────────────────
    │
    ▼
AIHighlightScreen
    │
    ├── Max highlights: [  5  ] (slider/input)
    └── Tap "Mulai Analisis"
            │
            ▼
      D-03 JobProgressBottomSheet
      ┌────────────────────────────────────┐
      │  🔄 AI Highlight Detection         │
      │  ████████░░░░░░░░░░░░  45%         │
      │  "Analyzing audio patterns..."     │
      │                        [Batalkan]  │
      └────────────────────────────────────┘
            │
            ▼
      [Selesai] → AIHighlightScreen (Results)
            │
            ├── Card: Highlight #1 — Score: 0.92 ⭐⭐⭐⭐⭐
            ├── Card: Highlight #2 — Score: 0.78 ⭐⭐⭐⭐
            ├── Card: Highlight #3 — Score: 0.65 ⭐⭐⭐
            └── [Export Pilihan] [Export Semua]


SCENE DETECTION (Free) ─────────────────────────────────────────────────
    │
    ▼
SceneDetectionScreen
    │
    └── Tap "Deteksi Scene"
            │
            ▼
      [Processing...]
            │
            ▼
      Grid Scene:
      ┌────────────────────────────────────┐
      │ [thumb] Scene 1  00:00 - 00:12     │
      │ [thumb] Scene 2  00:12 - 00:28     │
      │ [thumb] Scene 3  00:28 - 00:45     │
      │ [thumb] Scene 4  00:45 - 01:00     │
      └────────────────────────────────────┘
      [☑ Pilih Semua]  [Export Pilihan]


CLIP RESULT (Free — Watermark) ─────────────────────────────────────────
    │
    ▼
ClipDetailScreen
    │
    ├── Player [▶] — tampak watermark di pojok
    ├── ⚠ Banner kuning: "Clip ini memiliki watermark ClipForge"
    ├── Info: durasi, resolusi (720p max), ukuran
    └── [⬇ Download] [🗑 Hapus] [⭐ Upgrade untuk No Watermark]
```

---

## 5. Premium User Flow

### Keuntungan Premium
- Video unlimited, durasi tak terbatas
- Output hingga 4K
- Tanpa watermark
- Semua fitur AI (Speech, Object, Face, Gesture, Shorts)
- Queue priority tinggi (lebih cepat diproses)

### Premium User — Diagram Lengkap

```
╔══════════════════════════════════════════════════════════╗
║                   PREMIUM USER FLOW                      ║
╚══════════════════════════════════════════════════════════╝

Buka App
    │
    ▼
HomeScreen
    │
    ├── Badge: "⭐ Premium" di pojok profil
    ├── Tidak ada quota indicator (unlimited)
    └── Tap "Import Video"
            │
            ▼
      [Tidak ada batas harian]
            │
            ▼
      Paste URL → Preview
            │
            ▼
      [Semua durasi video diperbolehkan]
            │
            ▼
      VideoMetadataPreviewScreen
            │
            └─► Tap "Import & Pilih Aksi"
                    │
                    ▼
              ClipOptionsScreen (Premium View)
                    │
                    ├── [✅] Manual Clip
                    ├── [✅] AI Highlight
                    ├── [✅] Scene Detection
                    ├── [✅] Speech Search
                    ├── [✅] Object Tracking
                    ├── [✅] Face Tracking
                    ├── [✅] Gesture Tracking
                    └── [✅] Shorts Generator
                          (Semua tanpa ikon 🔒)


SPEECH SEARCH (Premium) ────────────────────────────────────────────────
    │
    ▼
SpeechSearchScreen
    │
    ├── Input: "Cari kata atau frasa di video"
    │          [  giveaway            ]
    ├── Padding clip: [  5  ] detik
    ├── Min confidence: [70%] (slider)
    └── Tap "Cari"
            │
            ▼
      [API: POST /jobs/speech-search]
            │
            ▼
      Processing: "Mentranskripsi audio dengan Whisper..."
            │
            ▼
      Hasil: Kata "giveaway" ditemukan 3 kali
      ┌────────────────────────────────────────┐
      │  "...mau ngasih [giveaway] buat..."    │
      │   ⏱ 02:15 → 02:20       [▶] [💾]      │
      ├────────────────────────────────────────┤
      │  "...ikutan [giveaway]-nya ya..."      │
      │   ⏱ 05:42 → 05:47       [▶] [💾]      │
      ├────────────────────────────────────────┤
      │  "...pemenang [giveaway] adalah..."    │
      │   ⏱ 08:03 → 08:08       [▶] [💾]      │
      └────────────────────────────────────────┘
      [Export Semua Hasil]


OBJECT TRACKING (Premium) ──────────────────────────────────────────────
    │
    ▼
ObjectTrackingScreen — Konfigurasi
    │
    ├── Pilih objek yang dicari:
    │   [☑ Person] [☑ Car] [☐ Cat] [☐ Dog]
    │   [☐ Motorcycle] [☐ Bicycle] [☐ Bus] [☐ Truck]
    ├── Min confidence: [50%]
    ├── Min durasi: [2.0] detik
    └── Tap "Mulai Tracking"
            │
            ▼
      Processing: "Menganalisis frame dengan YOLOv8..."
            │
            ▼
      Hasil Timeline:
      ┌────────────────────────────────────────┐
      │  👤 Person  00:00:12 - 00:00:35  [▶]  │
      │  🚗 Car     00:01:20 - 00:01:50  [▶]  │
      │  👤 Person  00:02:05 - 00:03:10  [▶]  │
      │  🚗 Car     00:04:15 - 00:04:45  [▶]  │
      └────────────────────────────────────────┘
      [Export Semua] [Export Pilihan]


FACE TRACKING (Premium) ────────────────────────────────────────────────
    │
    ▼
FaceTrackingScreen — Konfigurasi
    │
    ├── [☑] Auto-clip saat wajah muncul
    ├── [☐] Hanya wajah menghadap kamera
    ├── Padding clip: [3] detik
    └── Tap "Mulai Tracking"
            │
            ▼
      Processing: "Mendeteksi wajah dengan MediaPipe..."
            │
            ▼
      Hasil:
      ┌────────────────────────────────────────┐
      │  Wajah #1   00:00:05 - 00:01:30  [▶]  │
      │  Wajah #2   00:02:00 - 00:02:45  [▶]  │
      │  Wajah #1   00:03:10 - 00:04:00  [▶]  │
      └────────────────────────────────────────┘
      3 wajah terdeteksi, 3 clip dibuat
      [Export Semua] [Export Pilihan]


GESTURE TRACKING (Premium) ─────────────────────────────────────────────
    │
    ▼
GestureTrackingScreen — Konfigurasi
    │
    ├── Pilih gesture yang dicari:
    │   [☑ 👉 Pointing]    [☑ ✋ Hand Raised]
    │   [☑ 👋 Wave]        [☑ 👍 Thumbs Up]
    │   [☐ 👏 Clap]        [☐ 😐 Facing Camera]
    ├── Padding clip: [3] detik
    └── Tap "Mulai Tracking"
            │
            ▼
      Processing: "Mendeteksi pose dengan MediaPipe + YOLO..."
            │
            ▼
      Hasil Timeline:
      ┌────────────────────────────────────────┐
      │  👉 Pointing Right  00:02:15  94%  [▶] │
      │  ✋ Hand Raised      00:04:08  88%  [▶] │
      │  👍 Thumbs Up        00:08:22  91%  [▶] │
      │  👋 Wave             00:11:45  85%  [▶] │
      └────────────────────────────────────────┘
      4 gesture terdeteksi
      [Export Semua] [Export Pilihan]


SHORTS GENERATOR (Premium) ─────────────────────────────────────────────
    │
    ▼
ShortsGeneratorScreen — Konfigurasi
    │
    ├── Pilih clip sumber: [Pilih dari library ▼]
    ├── Aspect ratio: [9:16 ▼] (default TikTok/Reels/Shorts)
    ├── [☑] Auto-subtitle (Whisper)
    ├── [☑] Auto-center subject (YOLO)
    ├── [☑] Auto-zoom
    └── Tap "Generate Shorts"
            │
            ▼
      Processing:
      "Crop 9:16..." → "Deteksi subjek..." → "Generate subtitle..."
            │
            ▼
      Preview:
      ┌──────────────┐
      │              │
      │   [▶ Preview]│  ← Preview 9:16
      │              │
      │ [Teks sub-   │
      │  title burn] │
      │              │
      └──────────────┘
      Resolusi: 1080x1920 | Durasi: 00:45
      [⬇ Download MP4] [🔄 Regenerate]


CLIP RESULT (Premium — No Watermark) ───────────────────────────────────
    │
    ▼
ClipDetailScreen
    │
    ├── Player [▶] — bersih tanpa watermark
    ├── Info: durasi, resolusi (hingga 4K), ukuran
    └── [⬇ Download] [📤 Share] [🗑 Hapus]
```

---

## 6. Error States

### E-01 — Network Error

```
┌────────────────────────────────────────┐
│                                        │
│            📡                          │
│                                        │
│    Tidak ada koneksi internet          │
│                                        │
│  Periksa Wi-Fi atau data seluler       │
│  kamu, lalu coba lagi.                 │
│                                        │
│         [Coba Lagi]                    │
│                                        │
└────────────────────────────────────────┘
```
Tampil di: Semua screen yang butuh koneksi

---

### E-02 — URL YouTube Tidak Valid

```
[Input field dengan border merah]
 ❌ URL YouTube tidak valid

 Contoh URL yang benar:
 https://www.youtube.com/watch?v=xxxxx
 https://youtu.be/xxxxx
```
Tampil di: ImportVideoScreen

---

### E-03 — Video Tidak Bisa Diunduh

```
┌────────────────────────────────────────┐
│  ❌ Video Tidak Tersedia               │
│                                        │
│  Video ini tidak bisa diunduh.         │
│  Kemungkinan penyebab:                 │
│  • Video private atau dihapus          │
│  • Video hanya tersedia di region lain │
│  • Video membutuhkan login             │
│                                        │
│  [Coba URL Lain]                       │
└────────────────────────────────────────┘
```
Tampil di: ImportVideoScreen (setelah API error)

---

### E-04 — AI Job Gagal

```
┌────────────────────────────────────────┐
│  ❌ Analisis Gagal                     │
│                                        │
│  Terjadi kesalahan saat memproses      │
│  video kamu. Server kami sedang sibuk. │
│                                        │
│  Error: WORKER_TIMEOUT                 │
│                                        │
│  [🔄 Coba Lagi]  [Batal]              │
└────────────────────────────────────────┘
```
Tampil di: D-03 JobProgressBottomSheet (status = failed)

---

### E-05 — Storage Penuh

```
┌────────────────────────────────────────┐
│  ⚠ Penyimpanan Hampir Penuh            │
│                                        │
│  ████████████████░░░░  85% terpakai    │
│  4.5 GB / 5 GB                         │
│                                        │
│  Hapus beberapa clip lama atau         │
│  upgrade ke Premium (50 GB).           │
│                                        │
│  [Kelola Clip]  [Upgrade]              │
└────────────────────────────────────────┘
```
Tampil di: HomeScreen (banner) / ClipOptionsScreen (saat akan buat clip baru)

---

### E-06 — Session Expired / Token Invalid

```
[Dialog otomatis]
┌────────────────────────────────────────┐
│  🔐 Sesi Berakhir                      │
│                                        │
│  Login kamu sudah kedaluwarsa.         │
│  Silakan login ulang.                  │
│                                        │
│         [Login Ulang]                  │
└────────────────────────────────────────┘
```
Tampil di: Di atas semua screen (interceptor mendeteksi 401)

---

### E-07 — Daily Limit Reached (Free)

```
D-02 DailyLimitDialog
┌────────────────────────────────────────┐
│  📅 Batas Harian Tercapai              │
│                                        │
│  Kamu sudah menggunakan 3/3 kuota      │
│  video hari ini.                       │
│                                        │
│  Reset otomatis: besok pukul 00:00     │
│                                        │
│  Atau upgrade ke Premium untuk         │
│  import video tanpa batas.             │
│                                        │
│  [⭐ Upgrade Premium]  [Balik Besok]   │
└────────────────────────────────────────┘
```

---

### E-08 — Payment Failed

```
┌────────────────────────────────────────┐
│  ❌ Pembayaran Gagal                   │
│                                        │
│  Transaksi tidak berhasil diproses.    │
│                                        │
│  Kemungkinan penyebab:                 │
│  • Kartu ditolak                       │
│  • Saldo tidak cukup                   │
│  • Koneksi terputus saat transaksi     │
│                                        │
│  [Coba Lagi]  [Hubungi Support]        │
└────────────────────────────────────────┘
```
Tampil di: SubscriptionScreen (setelah Google Play Billing gagal)

---

### E-09 — Empty State (Belum Ada Data)

```
HomeScreen — Empty:
┌────────────────────────────────────────┐
│                                        │
│               🎬                       │
│                                        │
│   Belum ada video yang diimport        │
│                                        │
│   Mulai dengan import video YouTube    │
│   pertama kamu!                        │
│                                        │
│        [+ Import Video]                │
│                                        │
└────────────────────────────────────────┘

AIClipsScreen — Empty:
┌────────────────────────────────────────┐
│               ✂️                       │
│   Belum ada clip yang dibuat           │
│   Import video dan pilih aksi AI       │
│   untuk mulai membuat clip.            │
│        [+ Import Video]                │
└────────────────────────────────────────┘
```

---

## 7. Loading States

### L-01 — Splash / App Launch

```
┌────────────────────────────────────────┐
│                                        │
│                                        │
│           [Logo ClipForge]             │
│                                        │
│         C L I P F O R G E             │
│                                        │
│                                        │
│         ••••• (dots indicator)         │
│                                        │
└────────────────────────────────────────┘
```
Durasi: Cek token + user data (< 2 detik)

---

### L-02 — Import Video (Metadata Fetch)

```
ImportVideoScreen — setelah paste URL:

URL: [https://youtube.com/watch?v=xxxxx]
[Ambil Info Video...]

┌────────────────────────────────────────┐
│  ░░░░░░░░░░░░░░░░  (shimmer effect)    │
│  ░░░░░░░░░                             │
│  ░░░░░░░░░░░░░                         │
└────────────────────────────────────────┘
Shimmer placeholder thumbnail + info
```

---

### L-03 — Video Download Progress

```
V-01 VideoMetadataPreviewScreen setelah tap import:

[Thumbnail video]
Judul Video Ini Sedang Diproses

Status:  🔄 Mengunduh video...
         ████████░░░░░░░░  52%
         12.4 MB / 24.0 MB

[Lanjut ke Pilih Aksi] ← tetap bisa lanjut!
(video download berjalan di background)
```

---

### L-04 — AI Job Progress (Bottom Sheet)

```
D-03 JobProgressBottomSheet:

┌────────────────────────────────────────┐
│  ━━━━━━━━━━━━  (handle)                │
│                                        │
│  🔄 Gesture Tracking                   │
│                                        │
│  ████████████░░░░░░░░  65%             │
│                                        │
│  "Analyzing frame 2340/3600"           │
│                                        │
│  ⏱ Estimasi: 1 menit tersisa          │
│                                        │
│  [Premium: Antrian Prioritas Tinggi]   │
│  (atau "Free: Sedang Antri..." untuk free) │
│                                        │
│                          [Batalkan]    │
└────────────────────────────────────────┘

Polling interval: 3s → 5s → 10s → 30s (exponential backoff)
```

---

### L-05 — Clip Processing

```
ClipDetailScreen — saat clip sedang dirender:

[Placeholder thumbnail + animasi spin]

✂️ Clip sedang dibuat...
FFmpeg sedang memotong dan mengkode video kamu.

████░░░░░░░░░░░░░░░░  20%

Biasanya selesai dalam 10-30 detik.
```

---

### L-06 — List Loading (Skeleton)

```
AIClipsScreen — saat pertama load:

┌────────────────────────────────────────┐
│ [░░░░░░░░]  ░░░░░░░░░░░░░░            │
│             ░░░░░░░░░░                 │
│             ░░░░░░░  ░░░░              │
├────────────────────────────────────────┤
│ [░░░░░░░░]  ░░░░░░░░░░░░░░            │
│             ░░░░░░░░░░                 │
│             ░░░░░░░  ░░░░              │
├────────────────────────────────────────┤
│ [░░░░░░░░]  ░░░░░░░░░░░░░░            │
│             ░░░░░░░░░░                 │
└────────────────────────────────────────┘
(░ = shimmer/skeleton placeholder)
```

---

### L-07 — Subscription Verification

```
S-01 SubscriptionScreen setelah tap "Mulai Premium":

[Spinner]
Memverifikasi pembelian...
Mohon tunggu sebentar.

(layar non-interactable, tidak bisa di-back)
```

---

## 8. Wireframe — Setiap Screen

### A-01 OnboardingScreen

```
┌─────────────────────────────────────┐
│                                     │
│          [Logo ClipForge]           │
│                                     │
│     Selamat datang di ClipForge     │
│  AI Video Clipper untuk Android     │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│   Pilih mode pemrosesan AI:         │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  🖥 Server AI (Rekomendasi)   │  │  ← Selected state (outlined)
│  │  Lebih akurat, butuh internet │  │
│  │  Cocok untuk video 4K & panjang│ │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  📱 Local AI                  │  │
│  │  Tanpa upload, privasi lebih  │  │
│  │  Akurasi lebih rendah         │  │
│  └───────────────────────────────┘  │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│          [Mulai Sekarang]           │
│                                     │
│  Bisa diubah kapan saja di Settings │
│                                     │
└─────────────────────────────────────┘
```

---

### A-02 LoginScreen

```
┌─────────────────────────────────────┐
│                                     │
│          [Logo ClipForge]           │
│                                     │
│          Masuk ke ClipForge         │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  G  Lanjutkan dengan Google   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ─────────── atau ───────────       │
│                                     │
│  Email                              │
│  ┌───────────────────────────────┐  │
│  │  user@example.com             │  │
│  └───────────────────────────────┘  │
│                                     │
│  Password                           │
│  ┌───────────────────────────────┐  │
│  │  ••••••••              [👁]    │  │
│  └───────────────────────────────┘  │
│                                     │
│              [Masuk]                │
│                                     │
│     Belum punya akun? [Daftar]      │
│                                     │
└─────────────────────────────────────┘
```

---

### M-01 HomeScreen

```
┌─────────────────────────────────────┐
│  ClipForge           🔔  [Avatar]   │  ← TopAppBar
│                          ⭐Premium  │
├─────────────────────────────────────┤
│                                     │
│  Selamat datang, Java! 👋           │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  + Import Video YouTube       │  │  ← FAB / CTA Card
│  │  Paste URL dan mulai klip     │  │
│  └───────────────────────────────┘  │
│                                     │
│  Statistik Hari Ini                 │
│  ┌──────────┐  ┌──────────┐        │
│  │  3       │  │  12      │        │
│  │  Video   │  │  Clips   │        │
│  └──────────┘  └──────────┘        │
│                                     │
│  Video Terbaru                      │
│  ┌───────────────────────────────┐  │
│  │ [thumb] Judul Video 1    ▶   │  │
│  │         3 clip • 00:45:30    │  │
│  ├───────────────────────────────┤  │
│  │ [thumb] Judul Video 2    ▶   │  │
│  │         1 clip • 01:12:00    │  │
│  └───────────────────────────────┘  │
│                      [Lihat Semua]  │
│                                     │
│  Notifikasi                         │
│  ✅ AI Highlight selesai — 5 klip   │
│                                     │
├─────────────────────────────────────┤
│  🏠 Home  📥 Import  ✂ Clips  📁  ⚙│  ← Bottom Nav
└─────────────────────────────────────┘
```

---

### M-02 ImportVideoScreen (Paste URL)

```
┌─────────────────────────────────────┐
│  ←  Import Video YouTube            │
├─────────────────────────────────────┤
│                                     │
│  Paste URL video YouTube di bawah:  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  https://youtube.com/...  [✕] │  │
│  └───────────────────────────────┘  │
│                                     │
│           [🔍 Ambil Info]           │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  💡 Tips:                           │
│  • Buka YouTube → Share → Salin     │
│  • Atau paste dari clipboard         │
│  • Mendukung URL pendek youtu.be    │
│                                     │
│  [Free] Sisa kuota: 2/3 video hari  │  ← Hanya tampil untuk Free user
│                                     │
└─────────────────────────────────────┘
```

---

### V-01 VideoMetadataPreviewScreen

```
┌─────────────────────────────────────┐
│  ←  Preview Video                   │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │       [THUMBNAIL VIDEO]       │  │
│  │                               │  │
│  │         ▶                     │  │
│  └───────────────────────────────┘  │
│                                     │
│  Judul Video Yang Sangat Panjang    │
│  Dan Bisa Wrap Ke Baris Kedua       │
│                                     │
│  📺 RickAstleyVEVO                  │
│  ⏱ 03:32  •  🖥 1080p             │
│  📅 Diupload: 25 Okt 2009          │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  [Free] ⚠ Maks 60 detik            │  ← Hanya jika durasi > 60 detik
│  Video ini 3:32. Hanya 60 detik     │    dan user Free
│  pertama yang akan diproses.        │
│                                     │
│       [Import & Pilih Aksi]         │
│          [Batal]                    │
│                                     │
└─────────────────────────────────────┘
```

---

### V-02 ClipOptionsScreen

```
┌─────────────────────────────────────┐
│  ←  Pilih Aksi                      │
├─────────────────────────────────────┤
│  [thumb] Judul Video            │
│  ⏱ 03:32  🔄 Downloading (60%)    │  ← Status download inline
├─────────────────────────────────────┤
│                                     │
│  ✂ MANUAL                          │
│  ┌───────────────────────────────┐  │
│  │  ✂ Manual Clip                │  │
│  │  Potong video dengan start &  │  │
│  │  end time sendiri             │  │
│  └───────────────────────────────┘  │
│                                     │
│  🤖 AI — BASIC (Free)               │
│  ┌───────────────────────────────┐  │
│  │  ⭐ AI Highlight              │  │
│  │  Deteksi momen terbaik        │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  🎬 Scene Detection           │  │
│  │  Deteksi perpindahan scene    │  │
│  └───────────────────────────────┘  │
│                                     │
│  🚀 AI — PREMIUM                    │
│  ┌───────────────────────────────┐  │
│  │  🔍 Speech Search          🔒 │  │  ← 🔒 untuk Free user
│  │  Cari kata dalam video        │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  📦 Object Tracking        🔒 │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  😀 Face Tracking          🔒 │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  🤲 Gesture Tracking       🔒 │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  📱 Shorts Generator       🔒 │  │
│  │  Buat video TikTok/Reels      │  │
│  └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

### V-03 ManualClipScreen

```
┌─────────────────────────────────────┐
│  ←  Manual Clip                     │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │  [VIDEO PLAYER / THUMBNAIL]   │  │
│  │  ▶  ─────────────────────     │  │
│  │  00:00:30        01:30:00     │  │
│  └───────────────────────────────┘  │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  Mulai (Start Time)                 │
│  ┌───────────────────────────────┐  │
│  │  00 : 00 : 30                 │  │
│  └───────────────────────────────┘  │
│  [◄ -1s] [Set dari Player] [+1s ►] │
│                                     │
│  Selesai (End Time)                 │
│  ┌───────────────────────────────┐  │
│  │  00 : 01 : 30                 │  │
│  └───────────────────────────────┘  │
│  [◄ -1s] [Set dari Player] [+1s ►] │
│                                     │
│  Durasi: 1 menit 0 detik           │
│                                     │
│  Judul Clip (opsional)              │
│  ┌───────────────────────────────┐  │
│  │  Bagian menarik               │  │
│  └───────────────────────────────┘  │
│                                     │
│           [✂ Buat Clip]             │
│                                     │
└─────────────────────────────────────┘
```

---

### V-04 ClipDetailScreen

```
┌─────────────────────────────────────┐
│  ←  Detail Clip              [⋮]   │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │      [VIDEO PLAYER]           │  │
│  │        ▶  ⏸  ⏭              │  │
│  │  00:00:00 ─────────── 00:45   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ⚠ [Free] Clip ini memiliki        │  ← Hanya Free user
│  watermark ClipForge                │
│                                     │
│  Bagian menarik                     │
│  🎬 Highlight • ⭐ Score: 0.92     │
│                                     │
│  ⏱ 00:30 → 01:15 (45 detik)        │
│  🖥 720p • 📦 10.2 MB               │
│  ✅ Siap didownload                 │
│                                     │
│  Dari: Judul Video Sumbernya        │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  [⬇ Download]      [📤 Share]       │
│                                     │
│  [🗑 Hapus Clip]                    │
│                                     │
└─────────────────────────────────────┘
```

---

### F-01 AIHighlightScreen (Results)

```
┌─────────────────────────────────────┐
│  ←  AI Highlight                    │
├─────────────────────────────────────┤
│  ✅ Selesai — 5 highlight ditemukan  │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │  #1  ⭐⭐⭐⭐⭐  Score: 0.92   │  │
│  │  [thumb]  00:12:30 - 00:13:15 │  │
│  │  Durasi: 45 detik             │  │
│  │              [▶ Preview] [💾] │  │
│  ├───────────────────────────────┤  │
│  │  #2  ⭐⭐⭐⭐   Score: 0.78   │  │
│  │  [thumb]  00:25:00 - 00:25:40 │  │
│  │  Durasi: 40 detik             │  │
│  │              [▶ Preview] [💾] │  │
│  ├───────────────────────────────┤  │
│  │  #3  ⭐⭐⭐    Score: 0.65   │  │
│  │  [thumb]  00:42:15 - 00:43:00 │  │
│  │  Durasi: 45 detik             │  │
│  │              [▶ Preview] [💾] │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Export Semua]  [Export Pilihan]   │
│                                     │
└─────────────────────────────────────┘
```

---

### F-06 GestureTrackingScreen (Results)

```
┌─────────────────────────────────────┐
│  ←  Gesture Tracking                │
├─────────────────────────────────────┤
│  ✅ Selesai — 4 gesture ditemukan   │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │  👉 Pointing Right            │  │
│  │  ⏱ 00:02:15 • 94% confidence │  │
│  │  Clip: 00:02:12 → 00:02:18   │  │
│  │                   [▶] [💾]   │  │
│  ├───────────────────────────────┤  │
│  │  ✋ Hand Raised                │  │
│  │  ⏱ 00:04:08 • 88% confidence │  │
│  │  Clip: 00:04:05 → 00:04:11   │  │
│  │                   [▶] [💾]   │  │
│  ├───────────────────────────────┤  │
│  │  👍 Thumbs Up                 │  │
│  │  ⏱ 00:08:22 • 91% confidence │  │
│  │  Clip: 00:08:19 → 00:08:25   │  │
│  │                   [▶] [💾]   │  │
│  ├───────────────────────────────┤  │
│  │  👋 Wave                      │  │
│  │  ⏱ 00:11:45 • 85% confidence │  │
│  │  Clip: 00:11:42 → 00:11:48   │  │
│  │                   [▶] [💾]   │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Export Semua]  [Export Pilihan]   │
│                                     │
└─────────────────────────────────────┘
```

---

### S-01 SubscriptionScreen

```
┌─────────────────────────────────────┐
│  ←  ClipForge Premium               │
├─────────────────────────────────────┤
│                                     │
│         ⭐ Upgrade ke Premium        │
│   Buka semua fitur AI tanpa batas   │
│                                     │
│  ┌──────────────┬──────────────┐    │
│  │    FREE      │   PREMIUM    │    │
│  ├──────────────┼──────────────┤    │
│  │  3 video/hr  │  Unlimited   │    │
│  │  Max 60 dtk  │  No limit    │    │
│  │  720p max    │  4K output   │    │
│  │  Watermark   │  No mark     │    │
│  │  Highlight ✅│  Highlight ✅│    │
│  │  Scene ✅    │  Scene ✅    │    │
│  │  Speech ❌   │  Speech ✅   │    │
│  │  Object ❌   │  Object ✅   │    │
│  │  Face ❌     │  Face ✅     │    │
│  │  Gesture ❌  │  Gesture ✅  │    │
│  │  Shorts ❌   │  Shorts ✅   │    │
│  └──────────────┴──────────────┘    │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  ⭐ Premium Bulanan           │  │
│  │  Rp 79.000 / bulan            │  │
│  │  Batalkan kapan saja          │  │
│  └───────────────────────────────┘  │
│                                     │
│      [🚀 Mulai Premium Sekarang]    │
│                                     │
│    Diproses via Google Play         │
│    Aman & terenkripsi               │
│                                     │
└─────────────────────────────────────┘
```

---

### M-05 SettingsScreen

```
┌─────────────────────────────────────┐
│  ←  Pengaturan                      │
├─────────────────────────────────────┤
│                                     │
│  [Avatar]  Java Nih Deks            │
│            user@gmail.com           │
│            ⭐ Premium aktif         │
│                                     │
│  ─────────────────────────────────  │
│  PREFERENSI AI                      │
│                                     │
│  Mode AI                            │
│  [Server AI (Rekomendasi)    ▼]     │
│                                     │
│  Resolusi Output Default            │
│  [1080p                      ▼]     │
│                                     │
│  ─────────────────────────────────  │
│  LANGGANAN                          │
│                                     │
│  Status      ⭐ Premium             │
│  Aktif hingga  01 Jun 2026          │
│  [Kelola Langganan]                 │
│                                     │
│  ─────────────────────────────────  │
│  PENYIMPANAN                        │
│                                     │
│  Digunakan    4.5 GB / 50 GB        │
│  ████████████░░░░░░░░  9%           │
│  [Kelola Clip & Video]              │
│                                     │
│  ─────────────────────────────────  │
│  LAINNYA                            │
│                                     │
│  Tentang ClipForge                  │
│  Kebijakan Privasi                  │
│  Syarat & Ketentuan                 │
│                                     │
│  [Keluar]                           │
│                                     │
└─────────────────────────────────────┘
```

---

*ClipForge UI/UX Flow v1.0.0*
*Dibuat berdasarkan architecture.md, database.md, dan api.md*
*Siap digunakan sebagai referensi implementasi Jetpack Compose screens*
