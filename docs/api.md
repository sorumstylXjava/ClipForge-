# ClipForge — REST API Specification

**Version:** 1.0.0  
**Base URL:** `https://api.clipforge.app/v1`  
**Auth:** `Authorization: Bearer <supabase_access_token>`  
**Format:** JSON (`Content-Type: application/json`)

---

## Konvensi Umum

**Success response:**
```json
{ "data": { ... } }
```

**Error response:**
```json
{
  "error": "PLAN_REQUIRED",
  "message": "Fitur ini membutuhkan Premium Plan.",
  "status": 403
}
```

**Kode error umum:**

| Kode | HTTP | Keterangan |
|---|---|---|
| `UNAUTHORIZED` | 401 | Token tidak valid atau expired |
| `FORBIDDEN` | 403 | Tidak punya akses ke resource |
| `PLAN_REQUIRED` | 403 | Fitur membutuhkan Premium |
| `DAILY_LIMIT` | 429 | Kuota harian Free Plan habis |
| `RATE_LIMITED` | 429 | Terlalu banyak request |
| `NOT_FOUND` | 404 | Resource tidak ditemukan |
| `VALIDATION_ERROR` | 422 | Input tidak valid |

---

## 1. Authentication

### POST `/auth/register`
Daftarkan akun baru dengan email & password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "min8chars",
  "full_name": "John Doe"
}
```

**Response `201`:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "plan": "free"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### POST `/auth/login`
Login dengan email & password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "min8chars"
}
```

**Response `200`:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "plan": "free",
    "ai_mode": "server"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### POST `/auth/google`
Login dengan Google OAuth ID Token (dari Google Sign-In Android).

**Request Body:**
```json
{
  "id_token": "google_id_token_dari_android"
}
```

**Response `200`:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "full_name": "John Doe",
    "avatar_url": "https://...",
    "plan": "free"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "is_new_user": false
}
```

---

### POST `/auth/refresh`
Perbarui access token yang sudah expired.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200`:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### DELETE `/auth/logout`
Logout dan revoke token aktif.

**Request Body:** _kosong_

**Response `200`:**
```json
{ "message": "Logged out successfully." }
```

---

### GET `/auth/me`
Ambil profil user yang sedang login.

**Response `200`:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://...",
  "plan": "free",
  "ai_mode": "server",
  "preferred_resolution": "720p",
  "storage_used_bytes": 104857600,
  "storage_quota_bytes": 5368709120,
  "is_admin": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

### PATCH `/auth/me`
Update profil user (nama, preferensi AI mode, resolusi).

**Request Body:** _(semua field opsional)_
```json
{
  "full_name": "Jane Doe",
  "ai_mode": "local",
  "preferred_resolution": "1080p"
}
```

**Response `200`:** Profil terbaru (sama seperti `GET /auth/me`).

---

## 2. User

### GET `/users/{id}`
Detail user tertentu. Hanya bisa diakses oleh admin atau user itu sendiri.

**Response `200`:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "plan": "premium",
  "ai_mode": "server",
  "storage_used_bytes": 2147483648,
  "storage_quota_bytes": 53687091200,
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z",
  "last_login_at": "2026-05-30T10:00:00Z"
}
```

---

### GET `/users/me/notifications`
List notifikasi in-app milik user (job selesai, subscription expiring, dll).

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `unread_only` | boolean | false | Hanya notifikasi belum dibaca |
| `limit` | integer | 20 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "job_done",
      "title": "AI Highlight selesai!",
      "body": "Video kamu sudah diproses. 5 highlight tersedia.",
      "action_url": "/clips?job_id=uuid",
      "is_read": false,
      "created_at": "2026-05-31T08:00:00Z"
    }
  ],
  "total": 3,
  "unread_count": 3
}
```

---

### PATCH `/users/me/notifications/{id}/read`
Tandai satu notifikasi sebagai sudah dibaca.

**Response `200`:**
```json
{ "id": "uuid", "is_read": true, "read_at": "2026-05-31T09:00:00Z" }
```

---

## 3. Subscription

### GET `/subscriptions/me`
Status langganan user yang sedang aktif.

**Response `200`:**
```json
{
  "plan": "premium",
  "status": "active",
  "started_at": "2026-05-01T00:00:00Z",
  "expires_at": "2026-06-01T00:00:00Z",
  "payment_provider": "google_play",
  "provider_product_id": "premium_monthly",
  "entitlements": {
    "max_videos_per_day": null,
    "max_video_duration_seconds": null,
    "max_output_resolution": "4k",
    "watermark": false,
    "queue_priority": 1,
    "features": [
      "manual_clip", "highlight", "scene_detection",
      "object_tracking", "face_tracking", "gesture_tracking",
      "speech_search", "shorts_generator", "batch_processing"
    ]
  }
}
```

---

### GET `/subscriptions/me/history`
Riwayat semua langganan user.

**Response `200`:**
```json
{
  "subscriptions": [
    {
      "id": "uuid",
      "plan": "premium",
      "status": "expired",
      "started_at": "2026-04-01T00:00:00Z",
      "expires_at": "2026-05-01T00:00:00Z",
      "payment_provider": "google_play"
    }
  ]
}
```

---

### POST `/subscriptions/verify`
Verifikasi pembelian dari Google Play setelah transaksi berhasil di client.

**Request Body:**
```json
{
  "provider": "google_play",
  "purchase_token": "xxxxx",
  "product_id": "premium_monthly"
}
```

**Response `200`:**
```json
{
  "subscription": {
    "id": "uuid",
    "plan": "premium",
    "status": "active",
    "expires_at": "2026-06-31T00:00:00Z"
  },
  "user_plan_updated": true
}
```

---

### POST `/subscriptions/cancel`
Cancel langganan aktif. Akses Premium tetap berlaku hingga `expires_at`.

**Request Body:**
```json
{
  "reason": "too_expensive"
}
```

**Response `200`:**
```json
{
  "status": "cancelled",
  "access_until": "2026-06-01T00:00:00Z",
  "message": "Langganan dibatalkan. Premium aktif hingga 2026-06-01."
}
```

---

### GET `/subscriptions/plans`
Daftar paket tersedia (untuk tampilan UI upgrade).

**Response `200`:**
```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price": 0,
      "currency": "USD",
      "limits": {
        "videos_per_day": 3,
        "max_video_duration_seconds": 60,
        "max_resolution": "720p"
      },
      "features": ["manual_clip", "highlight", "scene_detection"],
      "watermark": true
    },
    {
      "id": "premium_monthly",
      "name": "Premium",
      "price": 4.99,
      "currency": "USD",
      "billing_period": "monthly",
      "limits": {},
      "features": [
        "manual_clip", "highlight", "scene_detection",
        "object_tracking", "face_tracking", "gesture_tracking",
        "speech_search", "shorts_generator", "batch_processing"
      ],
      "watermark": false
    }
  ]
}
```

---

## 4. Video

### POST `/videos/import`
Import video dari YouTube URL. Backend fetch metadata via yt-dlp dan mulai download asinkron.

> **Free Plan:** Maksimal 3 video/hari, maksimal durasi 60 detik.

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response `202`:**
```json
{
  "id": "uuid",
  "youtube_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "channel_name": "RickAstleyVEVO",
  "duration_seconds": 212,
  "resolution": "1080p",
  "status": "downloading"
}
```

---

### GET `/videos`
List semua video milik user, sorted by `created_at DESC`.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `status` | string | — | Filter: `pending`, `downloading`, `ready`, `error` |
| `limit` | integer | 20 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "videos": [
    {
      "id": "uuid",
      "youtube_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "thumbnail_url": "https://i.ytimg.com/...",
      "duration_seconds": 212,
      "resolution": "1080p",
      "status": "ready",
      "created_at": "2026-05-31T08:00:00Z"
    }
  ],
  "total": 12,
  "limit": 20,
  "offset": 0
}
```

---

### GET `/videos/{id}`
Detail lengkap satu video.

**Response `200`:**
```json
{
  "id": "uuid",
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "youtube_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "...",
  "channel_name": "RickAstleyVEVO",
  "thumbnail_url": "https://i.ytimg.com/...",
  "duration_seconds": 212,
  "resolution": "1080p",
  "width": 1920,
  "height": 1080,
  "fps": 25.0,
  "filesize_bytes": 52428800,
  "status": "ready",
  "download_finished_at": "2026-05-31T08:01:30Z",
  "created_at": "2026-05-31T08:00:00Z"
}
```

---

### GET `/videos/{id}/metadata`
Ambil metadata YouTube tanpa mengimport/download video (preview sebelum import).

**Response `200`:**
```json
{
  "youtube_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "channel_name": "RickAstleyVEVO",
  "duration_seconds": 212,
  "published_at": "2009-10-25T06:57:33Z",
  "available_resolutions": ["360p", "720p", "1080p"]
}
```

---

### DELETE `/videos/{id}`
Hapus video (soft delete). Semua clip dan job terkait juga ikut dihapus.

**Response `200`:**
```json
{ "message": "Video berhasil dihapus." }
```

---

## 5. Clip

### POST `/clips/manual`
Buat clip manual berdasarkan start & end time. Diproses via FFmpeg.

**Request Body:**
```json
{
  "video_id": "uuid",
  "start_time": 30.5,
  "end_time": 90.0,
  "title": "Bagian menarik",
  "resolution": "720p"
}
```

**Response `202`:**
```json
{
  "id": "uuid",
  "video_id": "uuid",
  "clip_type": "manual",
  "title": "Bagian menarik",
  "start_time": 30.5,
  "end_time": 90.0,
  "duration": 59.5,
  "status": "processing",
  "has_watermark": true,
  "created_at": "2026-05-31T09:00:00Z"
}
```

---

### GET `/clips`
List semua clip milik user.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `video_id` | uuid | — | Filter clip dari video tertentu |
| `clip_type` | string | — | Filter: `manual`, `highlight`, `speech`, `scene`, `object`, `face`, `gesture`, `short` |
| `status` | string | — | Filter: `processing`, `ready`, `error` |
| `limit` | integer | 20 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "clips": [
    {
      "id": "uuid",
      "video_id": "uuid",
      "title": "Bagian menarik",
      "clip_type": "manual",
      "start_time": 30.5,
      "end_time": 90.0,
      "duration": 59.5,
      "thumbnail_path": "https://storage.supabase.co/...",
      "resolution": "720p",
      "has_watermark": true,
      "highlight_score": null,
      "status": "ready",
      "created_at": "2026-05-31T09:00:00Z"
    }
  ],
  "total": 8,
  "limit": 20,
  "offset": 0
}
```

---

### GET `/clips/{id}`
Detail lengkap satu clip.

**Response `200`:**
```json
{
  "id": "uuid",
  "video_id": "uuid",
  "ai_job_id": null,
  "title": "Bagian menarik",
  "clip_type": "manual",
  "start_time": 30.5,
  "end_time": 90.0,
  "duration": 59.5,
  "output_path": "https://storage.supabase.co/...",
  "thumbnail_path": "https://storage.supabase.co/...",
  "filesize_bytes": 10485760,
  "resolution": "720p",
  "width": 1280,
  "height": 720,
  "fps": 25.0,
  "has_watermark": true,
  "is_vertical": false,
  "has_subtitle": false,
  "highlight_score": null,
  "status": "ready",
  "created_at": "2026-05-31T09:00:00Z"
}
```

---

### GET `/clips/{id}/download`
Ambil presigned download URL clip (berlaku 15 menit).

**Response `200`:**
```json
{
  "download_url": "https://storage.supabase.co/object/sign/...",
  "expires_in_seconds": 900,
  "filename": "clip_uuid_30s-90s.mp4"
}
```

---

### DELETE `/clips/{id}`
Hapus clip (soft delete).

**Response `200`:**
```json
{ "message": "Clip berhasil dihapus." }
```

---

## 6. AI Job

Semua AI job berjalan asinkron via Celery. Gunakan `GET /jobs/{id}` untuk polling status & progress.

> **Free Plan:** Hanya bisa akses `highlight` dan `scene_detection`. Fitur lain membutuhkan Premium.

---

### POST `/jobs/highlight`
Jalankan AI Highlight Detection. AI menganalisis audio, transkrip, dan scene change untuk menemukan momen terbaik.

**Request Body:**
```json
{
  "video_id": "uuid",
  "max_highlights": 5,
  "auto_clip": true
}
```

**Response `202`:**
```json
{
  "job_id": "uuid",
  "job_type": "highlight",
  "status": "queued",
  "priority": 5,
  "video_id": "uuid",
  "created_at": "2026-05-31T09:00:00Z"
}
```

---

### POST `/jobs/speech-search`
Cari kata/frasa dalam video menggunakan transkripsi Whisper. Otomatis buat clip di sekitar timestamp yang cocok.

> **Membutuhkan Premium.**

**Request Body:**
```json
{
  "video_id": "uuid",
  "query": "giveaway",
  "auto_clip": true,
  "clip_padding_seconds": 5,
  "min_confidence": 0.7
}
```

**Response `202`:** _(sama seperti response job lainnya)_

---

### POST `/jobs/scene-detection`
Deteksi perpindahan scene otomatis menggunakan PySceneDetect.

**Request Body:**
```json
{
  "video_id": "uuid",
  "auto_clip": false
}
```

**Response `202`:** _(sama seperti response job lainnya)_

---

### POST `/jobs/object-tracking`
Deteksi dan tracking objek menggunakan YOLOv8. Auto-clip saat objek muncul.

> **Membutuhkan Premium.**

**Request Body:**
```json
{
  "video_id": "uuid",
  "classes": ["person", "car", "cat"],
  "auto_clip": true,
  "clip_padding_seconds": 3,
  "min_confidence": 0.5,
  "min_duration_seconds": 2.0
}
```

Nilai `classes` yang tersedia: `person`, `car`, `motorcycle`, `cat`, `dog`, `bicycle`, `bus`, `truck`.

**Response `202`:** _(sama seperti response job lainnya)_

---

### POST `/jobs/face-tracking`
Deteksi dan tracking wajah menggunakan MediaPipe. Auto-clip saat wajah muncul.

> **Membutuhkan Premium.**

**Request Body:**
```json
{
  "video_id": "uuid",
  "auto_clip": true,
  "clip_padding_seconds": 3,
  "front_facing_only": false
}
```

**Response `202`:** _(sama seperti response job lainnya)_

---

### POST `/jobs/gesture-tracking`
Deteksi gesture menggunakan MediaPipe + YOLO Pose. Auto-clip saat gesture terdeteksi.

> **Membutuhkan Premium.**

**Request Body:**
```json
{
  "video_id": "uuid",
  "gestures": ["pointing", "hand_raised", "thumbs_up", "wave", "clap", "facing_camera"],
  "auto_clip": true,
  "clip_padding_seconds": 3
}
```

Nilai `gestures` yang tersedia: `pointing`, `hand_raised`, `wave`, `thumbs_up`, `clap`, `facing_camera`.

**Response `202`:** _(sama seperti response job lainnya)_

---

### POST `/jobs/shorts`
Generate video vertikal 9:16 otomatis (TikTok/Reels/Shorts). AI auto-crop, auto-subtitle, auto-center subject.

> **Membutuhkan Premium.**

**Request Body:**
```json
{
  "video_id": "uuid",
  "source_clip_id": "uuid",
  "aspect_ratio": "9:16",
  "auto_subtitle": true,
  "subtitle_font": "default",
  "auto_center": true,
  "auto_zoom": true
}
```

**Response `202`:** _(sama seperti response job lainnya)_

---

### GET `/jobs/{id}`
Polling status dan progress satu AI job.

**Response `200`:**
```json
{
  "id": "uuid",
  "job_type": "gesture_tracking",
  "status": "processing",
  "priority": 1,
  "progress": 65,
  "progress_message": "Analyzing frame 2340/3600",
  "video_id": "uuid",
  "processing_mode": "server",
  "created_at": "2026-05-31T09:00:00Z",
  "started_at": "2026-05-31T09:00:05Z",
  "finished_at": null,
  "error_message": null
}
```

Status lifecycle: `queued` → `processing` → `done` | `failed` | `cancelled`

---

### GET `/jobs/{id}/results`
Ambil hasil lengkap job setelah `status = "done"`.

**Response `200`:**
```json
{
  "job_id": "uuid",
  "job_type": "gesture_tracking",
  "status": "done",
  "result_count": 4,
  "results": [
    {
      "id": "uuid",
      "result_type": "gesture",
      "timestamp_point": 135.0,
      "label": "Person pointing right",
      "gesture_type": "pointing",
      "direction": "right",
      "score": 0.94,
      "clip_id": "uuid",
      "clip_start_time": 132.0,
      "clip_end_time": 138.0
    },
    {
      "id": "uuid",
      "result_type": "gesture",
      "timestamp_point": 248.5,
      "label": "Hand raised",
      "gesture_type": "hand_raised",
      "direction": null,
      "score": 0.88,
      "clip_id": "uuid",
      "clip_start_time": 245.5,
      "clip_end_time": 251.5
    }
  ]
}
```

Untuk `job_type = "highlight"`, tiap result berisi `start_time`, `end_time`, `total_score`, dan breakdown skor.
Untuk `job_type = "scene_detection"`, tiap result berisi `start_time`, `end_time`, `scene_index`, dan `thumbnail_path`.
Untuk `job_type = "speech_search"`, tiap result berisi `timestamp_point`, `matched_word`, dan `context_text`.

---

### GET `/jobs`
List semua AI job milik user.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `video_id` | uuid | — | Filter job dari video tertentu |
| `job_type` | string | — | Filter berdasarkan tipe job |
| `status` | string | — | Filter berdasarkan status |
| `limit` | integer | 20 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "jobs": [
    {
      "id": "uuid",
      "job_type": "highlight",
      "status": "done",
      "progress": 100,
      "video_id": "uuid",
      "result_count": 5,
      "created_at": "2026-05-31T09:00:00Z",
      "finished_at": "2026-05-31T09:02:30Z"
    }
  ],
  "total": 7,
  "limit": 20,
  "offset": 0
}
```

---

### DELETE `/jobs/{id}`
Cancel job yang masih `queued`. Job yang sedang `processing` tidak bisa di-cancel.

**Response `200`:**
```json
{ "message": "Job berhasil dibatalkan.", "status": "cancelled" }
```

---

## 7. Payment

### GET `/payments/me`
Riwayat transaksi user.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `status` | string | — | Filter: `success`, `pending`, `failed`, `refunded` |
| `limit` | integer | 20 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "payments": [
    {
      "id": "uuid",
      "amount": 4.99,
      "currency": "USD",
      "provider": "google_play",
      "provider_product_id": "premium_monthly",
      "status": "success",
      "paid_at": "2026-05-01T00:00:00Z",
      "created_at": "2026-05-01T00:00:00Z"
    }
  ],
  "total": 3
}
```

---

### GET `/payments/{id}`
Detail satu transaksi.

**Response `200`:**
```json
{
  "id": "uuid",
  "subscription_id": "uuid",
  "amount": 4.99,
  "currency": "USD",
  "amount_usd": 4.99,
  "provider": "google_play",
  "provider_tx_id": "GPA.xxxx",
  "provider_order_id": "GPA.xxxx",
  "provider_product_id": "premium_monthly",
  "status": "success",
  "failure_reason": null,
  "paid_at": "2026-05-01T00:00:00Z",
  "refunded_at": null,
  "created_at": "2026-05-01T00:00:00Z"
}
```

---

## 8. Admin

Semua endpoint `/admin/*` membutuhkan `users.is_admin = true`. Jika tidak, response `403 FORBIDDEN`.

---

### GET `/admin/users`
List semua user dengan filter dan pagination.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `plan` | string | — | Filter: `free`, `premium` |
| `search` | string | — | Cari berdasarkan email atau nama |
| `is_active` | boolean | — | Filter user aktif/nonaktif |
| `limit` | integer | 50 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "plan": "premium",
      "is_active": true,
      "storage_used_bytes": 2147483648,
      "created_at": "2026-01-01T00:00:00Z",
      "last_login_at": "2026-05-30T10:00:00Z"
    }
  ],
  "total": 1523,
  "limit": 50,
  "offset": 0
}
```

---

### PUT `/admin/users/{id}/plan`
Override plan user secara manual (untuk testing, kompensasi, dll).

**Request Body:**
```json
{
  "plan": "premium",
  "reason": "Manual grant - support ticket #123",
  "expires_at": "2026-07-01T00:00:00Z"
}
```

**Response `200`:**
```json
{
  "user_id": "uuid",
  "plan": "premium",
  "expires_at": "2026-07-01T00:00:00Z",
  "updated_by": "admin_uuid"
}
```

---

### PUT `/admin/users/{id}/suspend`
Suspend atau aktifkan kembali akun user.

**Request Body:**
```json
{
  "is_active": false,
  "reason": "Melanggar Terms of Service"
}
```

**Response `200`:**
```json
{ "user_id": "uuid", "is_active": false }
```

---

### GET `/admin/subscriptions`
List semua subscription di sistem.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `status` | string | `active` | Filter status |
| `provider` | string | — | Filter: `google_play`, `stripe`, `manual` |
| `limit` | integer | 50 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "subscriptions": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_email": "user@example.com",
      "plan": "premium",
      "status": "active",
      "started_at": "2026-05-01T00:00:00Z",
      "expires_at": "2026-06-01T00:00:00Z",
      "payment_provider": "google_play"
    }
  ],
  "total": 342
}
```

---

### GET `/admin/jobs`
Monitoring job queue real-time.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `status` | string | — | Filter: `queued`, `processing`, `done`, `failed` |
| `job_type` | string | — | Filter berdasarkan tipe job |
| `limit` | integer | 50 | Maks per halaman |
| `offset` | integer | 0 | Pagination offset |

**Response `200`:**
```json
{
  "summary": {
    "queued": 12,
    "processing": 4,
    "done_today": 287,
    "failed_today": 3
  },
  "by_type": [
    { "job_type": "highlight", "queued": 8, "processing": 2 },
    { "job_type": "gesture_tracking", "queued": 4, "processing": 2 }
  ],
  "jobs": [
    {
      "id": "uuid",
      "job_type": "highlight",
      "status": "queued",
      "priority": 5,
      "user_id": "uuid",
      "video_id": "uuid",
      "queued_at": "2026-05-31T09:00:00Z",
      "wait_seconds": 45
    }
  ],
  "total": 16
}
```

---

### POST `/admin/jobs/{id}/retry`
Re-queue job yang berstatus `failed`.

**Request Body:** _kosong_

**Response `200`:**
```json
{ "job_id": "uuid", "status": "queued", "message": "Job berhasil di-retry." }
```

---

### GET `/admin/stats`
Statistik penggunaan agregat.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `from` | date | 30 hari lalu | Format: `YYYY-MM-DD` |
| `to` | date | hari ini | Format: `YYYY-MM-DD` |

**Response `200`:**
```json
{
  "period": { "from": "2026-05-01", "to": "2026-05-31" },
  "users": {
    "total": 1523,
    "new_this_period": 87,
    "premium": 342,
    "free": 1181
  },
  "usage": {
    "videos_imported": 4210,
    "clips_exported": 9830,
    "ai_jobs_submitted": 6540
  },
  "revenue": {
    "total_usd": 1707.58,
    "currency": "USD"
  },
  "daily": [
    {
      "date": "2026-05-31",
      "videos_imported": 142,
      "clips_exported": 321,
      "ai_jobs_submitted": 215,
      "new_users": 4
    }
  ]
}
```

---

### GET `/admin/ai-usage`
Log penggunaan per model AI untuk cost tracking dan monitoring GPU.

**Query Params:**

| Param | Tipe | Default | Keterangan |
|---|---|---|---|
| `from` | date | 30 hari lalu | Format: `YYYY-MM-DD` |
| `to` | date | hari ini | Format: `YYYY-MM-DD` |

**Response `200`:**
```json
{
  "period": { "from": "2026-05-01", "to": "2026-05-31" },
  "by_model": [
    {
      "model": "whisper-base",
      "job_count": 1230,
      "total_gpu_seconds": 24600,
      "avg_gpu_seconds_per_job": 20.0
    },
    {
      "model": "yolov8n",
      "job_count": 870,
      "total_gpu_seconds": 43500,
      "avg_gpu_seconds_per_job": 50.0
    },
    {
      "model": "mediapipe-pose",
      "job_count": 540,
      "total_gpu_seconds": 16200,
      "avg_gpu_seconds_per_job": 30.0
    }
  ],
  "top_consumers": [
    {
      "user_id": "uuid",
      "email": "heavyuser@example.com",
      "plan": "premium",
      "total_gpu_seconds": 3600,
      "job_count": 42
    }
  ]
}
```

---

*ClipForge API Specification v1.0.0*
*Base URL: `https://api.clipforge.app/v1`*
