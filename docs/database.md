# ClipForge — Database Schema

**Version:** 1.0.0
**Last Updated:** 2026-05-31
**Engine:** PostgreSQL 16
**ORM:** SQLAlchemy 2.x (Async)
**Migration Tool:** Alembic

---

## Table of Contents

1. [Overview](#1-overview)
2. [ERD — Entity Relationship Diagram](#2-erd--entity-relationship-diagram)
3. [Enums & Domain Values](#3-enums--domain-values)
4. [Tables](#4-tables)
   - [users](#41-users)
   - [subscriptions](#42-subscriptions)
   - [videos](#43-videos)
   - [transcripts](#44-transcripts)
   - [transcript_words](#45-transcript_words)
   - [clips](#46-clips)
   - [ai_jobs](#47-ai_jobs)
   - [job_results](#48-job_results)
   - [scenes](#49-scenes)
   - [object_detections](#410-object_detections)
   - [face_detections](#411-face_detections)
   - [gesture_detections](#412-gesture_detections)
   - [highlights](#413-highlights)
   - [payments](#414-payments)
   - [usage_logs](#415-usage_logs)
   - [api_keys](#416-api_keys)
   - [notifications](#417-notifications)
5. [Indexes](#5-indexes)
6. [Constraints & Business Rules](#6-constraints--business-rules)
7. [JSONB Column Schemas](#7-jsonb-column-schemas)
8. [Relationships Summary](#8-relationships-summary)
9. [Common Queries](#9-common-queries)
10. [Migration Strategy](#10-migration-strategy)

---

## 1. Overview

ClipForge menggunakan **PostgreSQL 16** sebagai satu-satunya database utama. Tidak ada pemisahan antara read replica dan primary di tahap MVP — cukup ditambahkan di Phase 3.

### Prinsip Desain

| Prinsip | Keputusan |
|---|---|
| **Primary Key** | `UUID v4` untuk semua tabel (non-sequential, aman untuk expose ke client) |
| **Timestamps** | `TIMESTAMPTZ` (UTC) untuk semua kolom waktu |
| **Soft Delete** | `deleted_at TIMESTAMPTZ NULL` — tidak ada hard delete pada entitas utama |
| **Enum storage** | `TEXT` dengan `CHECK CONSTRAINT` — lebih mudah di-migrate dibanding PostgreSQL ENUM type |
| **Flexible data** | `JSONB` untuk metadata AI yang strukturnya bisa berubah |
| **Cascade** | `ON DELETE CASCADE` hanya untuk child data yang tidak punya nilai independen |
| **Timezone** | Semua waktu disimpan UTC, konversi dilakukan di application layer |

### Statistik Tabel

| # | Tabel | Kategori | Baris/hari (estimasi) |
|---|---|---|---|
| 1 | `users` | Core | ~50 |
| 2 | `subscriptions` | Core | ~10 |
| 3 | `videos` | Core | ~150 |
| 4 | `transcripts` | AI Output | ~100 |
| 5 | `transcript_words` | AI Output | ~500,000 |
| 6 | `clips` | Core | ~400 |
| 7 | `ai_jobs` | Queue | ~200 |
| 8 | `job_results` | AI Output | ~2,000 |
| 9 | `scenes` | AI Output | ~1,000 |
| 10 | `object_detections` | AI Output | ~5,000 |
| 11 | `face_detections` | AI Output | ~5,000 |
| 12 | `gesture_detections` | AI Output | ~3,000 |
| 13 | `highlights` | AI Output | ~500 |
| 14 | `payments` | Finance | ~10 |
| 15 | `usage_logs` | Analytics | ~350 |
| 16 | `api_keys` | Auth | ~5 |
| 17 | `notifications` | System | ~200 |

---

## 2. ERD — Entity Relationship Diagram

```
                              ┌──────────────────┐
                              │      users       │
                              │──────────────────│
                              │ PK id (uuid)     │
                              │    supabase_uid  │
                              │    email         │
                              │    plan          │
                              │    is_admin      │
                              └────────┬─────────┘
                                       │
           ┌───────────────────────────┼──────────────────────────────┐
           │                           │                              │
           │ 1:N                       │ 1:N                          │ 1:N
           ▼                           ▼                              ▼
  ┌─────────────────┐        ┌──────────────────┐          ┌──────────────────┐
  │  subscriptions  │        │     videos       │          │   usage_logs     │
  │─────────────────│        │──────────────────│          │──────────────────│
  │ PK id           │        │ PK id            │          │ PK id            │
  │ FK user_id      │        │ FK user_id       │          │ FK user_id       │
  │    plan         │        │    youtube_id    │          │    action        │
  │    status       │        │    status        │          │    date          │
  │    expires_at   │        │    file_path     │          └──────────────────┘
  └────────┬────────┘        └────────┬─────────┘
           │                          │
           │ 1:N                      │ 1:N
           ▼                          │
  ┌─────────────────┐                 │
  │    payments     │                 │
  │─────────────────│                 │
  │ PK id           │                 │
  │ FK user_id      │                 │
  │ FK sub_id       │                 │
  │    amount       │                 │
  │    status       │                 │
  └─────────────────┘                 │
                                      │
          ┌───────────────────────────┼──────────────────────────────┐
          │ 1:1                       │ 1:N                          │ 1:N
          ▼                           ▼                              ▼
  ┌──────────────────┐    ┌──────────────────┐           ┌──────────────────┐
  │   transcripts    │    │    ai_jobs       │           │     clips        │
  │──────────────────│    │──────────────────│           │──────────────────│
  │ PK id            │    │ PK id            │           │ PK id            │
  │ FK video_id (UQ) │    │ FK video_id      │           │ FK video_id      │
  │    full_text     │    │ FK user_id       │           │ FK user_id       │
  │    language      │    │    job_type      │           │ FK ai_job_id?    │
  │    model_used    │    │    status        │           │    clip_type     │
  └────────┬─────────┘    │    priority      │           │    start_time    │
           │              │    progress      │           │    end_time      │
           │ 1:N          └────────┬─────────┘           │    output_path   │
           ▼                      │                      └──────────────────┘
  ┌──────────────────┐            │ 1:N
  │ transcript_words │            ▼
  │──────────────────│   ┌──────────────────┐
  │ PK id            │   │   job_results    │
  │ FK transcript_id │   │──────────────────│
  │    word          │   │ PK id            │
  │    start_time    │   │ FK ai_job_id     │
  │    end_time      │   │ FK clip_id?      │
  │    confidence    │   │    result_type   │
  └──────────────────┘   │    start_time    │
                         │    end_time      │
                         │    label         │
                         │    score         │
                         └────────┬─────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼ (via video_id)        ▼ (via video_id)        ▼ (via video_id)
  ┌──────────────┐       ┌──────────────────┐    ┌──────────────────┐
  │   scenes     │       │object_detections │    │face_detections   │
  │──────────────│       │──────────────────│    │──────────────────│
  │ PK id        │       │ PK id            │    │ PK id            │
  │ FK video_id  │       │ FK video_id      │    │ FK video_id      │
  │ FK ai_job_id │       │ FK ai_job_id     │    │ FK ai_job_id     │
  │    scene_idx │       │    class_name    │    │    face_id       │
  │    start_t   │       │    start_time    │    │    start_time    │
  │    end_t     │       │    end_time      │    │    end_time      │
  └──────────────┘       │    confidence   │    └──────────────────┘
                         └──────────────────┘
                                               ┌──────────────────┐
                                               │gesture_detections│
                                               │──────────────────│
                                               │ PK id            │
                                               │ FK video_id      │
                                               │ FK ai_job_id     │
                                               │    gesture_type  │
                                               │    timestamp     │
                                               │    confidence    │
                                               └──────────────────┘
```

---

## 3. Enums & Domain Values

Semua enum disimpan sebagai `TEXT` dengan `CHECK CONSTRAINT`, bukan tipe ENUM PostgreSQL, agar mudah ditambah nilainya tanpa DDL migration.

### `user_plan`
```
'free' | 'premium'
```

### `user_ai_mode`
```
'local' | 'server'
```

### `subscription_status`
```
'active' | 'expired' | 'cancelled' | 'trial' | 'paused'
```

### `subscription_plan`
```
'free' | 'premium'
```

### `payment_provider`
```
'google_play' | 'stripe' | 'manual'
```

### `payment_status`
```
'pending' | 'success' | 'failed' | 'refunded' | 'disputed'
```

### `video_status`
```
'pending' | 'downloading' | 'ready' | 'error' | 'deleted'
```

### `video_resolution`
```
'360p' | '480p' | '720p' | '1080p' | '1440p' | '4k'
```

### `clip_type`
```
'manual' | 'highlight' | 'speech' | 'scene' | 'object' | 'face' | 'gesture' | 'short'
```

### `ai_job_type`
```
'highlight' | 'speech_search' | 'scene_detection' | 'object_tracking'
| 'face_tracking' | 'gesture_tracking' | 'shorts_generation' | 'transcription'
```

### `ai_job_status`
```
'queued' | 'processing' | 'done' | 'failed' | 'cancelled'
```

### `job_result_type`
```
'highlight' | 'speech_match' | 'scene' | 'object' | 'face' | 'gesture' | 'short'
```

### `object_class`
```
'person' | 'car' | 'motorcycle' | 'cat' | 'dog' | 'bicycle' | 'bus' | 'truck'
```

### `gesture_type`
```
'pointing' | 'hand_raised' | 'wave' | 'thumbs_up' | 'clap' | 'facing_camera'
```

### `notification_type`
```
'job_done' | 'job_failed' | 'subscription_expiring' | 'subscription_expired'
| 'new_feature' | 'system'
```

### `usage_action`
```
'video_import' | 'clip_export' | 'ai_job_submit' | 'storage_upload'
```

---

## 4. Tables

### 4.1 `users`

Tabel inti yang menyimpan data pengguna ClipForge. Setiap user terhubung ke Supabase Auth via `supabase_uid`.

```sql
CREATE TABLE users (
    -- Identity
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_uid    TEXT            NOT NULL,
    email           TEXT            NOT NULL,
    full_name       TEXT,
    avatar_url      TEXT,           -- URL gambar profil (dari Google/Supabase)
    phone           TEXT,

    -- Plan & Configuration
    plan            TEXT            NOT NULL DEFAULT 'free'
                                    CHECK (plan IN ('free', 'premium')),
    ai_mode         TEXT            NOT NULL DEFAULT 'server'
                                    CHECK (ai_mode IN ('local', 'server')),
    preferred_lang  TEXT            NOT NULL DEFAULT 'en',  -- ISO 639-1
    preferred_resolution TEXT       DEFAULT '720p'
                                    CHECK (preferred_resolution IN ('360p', '480p', '720p', '1080p', '1440p', '4k')),

    -- Status
    is_admin        BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN         NOT NULL DEFAULT FALSE,  -- email verified

    -- Storage Usage
    storage_used_bytes BIGINT       NOT NULL DEFAULT 0,      -- bytes terpakai di Supabase Storage
    storage_quota_bytes BIGINT      NOT NULL DEFAULT 5368709120, -- 5 GB default (free)

    -- Timestamps
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ     -- soft delete
);

-- Constraints
ALTER TABLE users ADD CONSTRAINT uq_users_supabase_uid UNIQUE (supabase_uid);
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT chk_users_storage CHECK (storage_used_bytes >= 0);
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `supabase_uid` | TEXT | NOT NULL | — | FK ke Supabase Auth, UNIQUE |
| `email` | TEXT | NOT NULL | — | UNIQUE |
| `full_name` | TEXT | NULL | — | Display name |
| `avatar_url` | TEXT | NULL | — | URL foto profil |
| `phone` | TEXT | NULL | — | Opsional |
| `plan` | TEXT | NOT NULL | 'free' | Enum: free/premium |
| `ai_mode` | TEXT | NOT NULL | 'server' | Enum: local/server |
| `preferred_lang` | TEXT | NOT NULL | 'en' | ISO 639-1 |
| `preferred_resolution` | TEXT | NULL | '720p' | Output default |
| `is_admin` | BOOLEAN | NOT NULL | FALSE | Admin flag |
| `is_active` | BOOLEAN | NOT NULL | TRUE | Bisa di-suspend |
| `is_verified` | BOOLEAN | NOT NULL | FALSE | Email verified |
| `storage_used_bytes` | BIGINT | NOT NULL | 0 | Total storage terpakai |
| `storage_quota_bytes` | BIGINT | NOT NULL | 5368709120 | 5GB free, 50GB premium |
| `last_login_at` | TIMESTAMPTZ | NULL | — | Tracking aktifitas |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | Auto-update via trigger |
| `deleted_at` | TIMESTAMPTZ | NULL | — | Soft delete |

---

### 4.2 `subscriptions`

Menyimpan riwayat langganan pengguna. Setiap user bisa punya banyak record (riwayat), tapi hanya satu `active` pada satu waktu.

```sql
CREATE TABLE subscriptions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Plan Info
    plan                TEXT        NOT NULL
                                    CHECK (plan IN ('free', 'premium')),
    status              TEXT        NOT NULL
                                    CHECK (status IN ('active', 'expired', 'cancelled', 'trial', 'paused')),

    -- Period
    started_at          TIMESTAMPTZ NOT NULL,
    expires_at          TIMESTAMPTZ,                -- NULL = tidak pernah expired (lifetime)
    trial_ends_at       TIMESTAMPTZ,                -- NULL = bukan trial

    -- Payment Provider
    payment_provider    TEXT
                                    CHECK (payment_provider IN ('google_play', 'stripe', 'manual')),
    provider_sub_id     TEXT,                       -- ID dari Google Play / Stripe
    provider_product_id TEXT,                       -- SKU product ID (misal: 'premium_monthly')
    provider_data       JSONB,                      -- Raw webhook payload dari provider

    -- Cancellation
    cancelled_at        TIMESTAMPTZ,
    cancellation_reason TEXT,

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Hanya boleh ada satu active subscription per user
CREATE UNIQUE INDEX uq_subscriptions_active_per_user
    ON subscriptions (user_id)
    WHERE status = 'active';
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `user_id` | UUID | NOT NULL | — | FK → users.id CASCADE |
| `plan` | TEXT | NOT NULL | — | Enum: free/premium |
| `status` | TEXT | NOT NULL | — | Enum: active/expired/cancelled/trial/paused |
| `started_at` | TIMESTAMPTZ | NOT NULL | — | Kapan aktif mulai |
| `expires_at` | TIMESTAMPTZ | NULL | — | NULL = lifetime |
| `trial_ends_at` | TIMESTAMPTZ | NULL | — | Kapan trial berakhir |
| `payment_provider` | TEXT | NULL | — | Enum: google_play/stripe/manual |
| `provider_sub_id` | TEXT | NULL | — | External subscription ID |
| `provider_product_id` | TEXT | NULL | — | SKU produk di store |
| `provider_data` | JSONB | NULL | — | Raw payload dari provider |
| `cancelled_at` | TIMESTAMPTZ | NULL | — | Waktu cancel |
| `cancellation_reason` | TEXT | NULL | — | Alasan cancel |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | |

---

### 4.3 `videos`

Menyimpan data video YouTube yang diimport oleh pengguna.

```sql
CREATE TABLE videos (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- YouTube Metadata
    youtube_url         TEXT        NOT NULL,
    youtube_id          TEXT        NOT NULL,        -- contoh: 'dQw4w9WgXcQ'
    title               TEXT,
    description         TEXT,
    channel_name        TEXT,
    channel_id          TEXT,
    thumbnail_url       TEXT,
    published_at        TIMESTAMPTZ,                 -- upload asli di YouTube

    -- Technical
    duration_seconds    INTEGER     CHECK (duration_seconds > 0),
    width               INTEGER,
    height              INTEGER,
    fps                 NUMERIC(5,2),
    resolution          TEXT        CHECK (resolution IN ('360p', '480p', '720p', '1080p', '1440p', '4k')),
    filesize_bytes      BIGINT,
    codec_video         TEXT,                        -- misal: 'h264', 'vp9'
    codec_audio         TEXT,                        -- misal: 'aac', 'opus'
    bitrate_kbps        INTEGER,

    -- Storage
    file_path           TEXT,                        -- Supabase Storage path
    thumbnail_path      TEXT,                        -- Generated thumbnail path

    -- Status
    status              TEXT        NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending', 'downloading', 'ready', 'error', 'deleted')),
    error_message       TEXT,

    -- Timestamps
    download_started_at TIMESTAMPTZ,
    download_finished_at TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ                  -- soft delete
);

-- Satu user tidak bisa import URL yang sama dua kali (hanya yang belum dihapus)
CREATE UNIQUE INDEX uq_videos_user_youtube
    ON videos (user_id, youtube_id)
    WHERE deleted_at IS NULL;
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `user_id` | UUID | NOT NULL | — | FK → users.id CASCADE |
| `youtube_url` | TEXT | NOT NULL | — | URL lengkap |
| `youtube_id` | TEXT | NOT NULL | — | Video ID YouTube (11 karakter) |
| `title` | TEXT | NULL | — | Judul dari yt-dlp |
| `description` | TEXT | NULL | — | Deskripsi video |
| `channel_name` | TEXT | NULL | — | Nama channel |
| `channel_id` | TEXT | NULL | — | Channel ID YouTube |
| `thumbnail_url` | TEXT | NULL | — | URL thumbnail YouTube |
| `published_at` | TIMESTAMPTZ | NULL | — | Waktu upload ke YouTube |
| `duration_seconds` | INTEGER | NULL | — | Durasi video dalam detik |
| `width` | INTEGER | NULL | — | Lebar frame (px) |
| `height` | INTEGER | NULL | — | Tinggi frame (px) |
| `fps` | NUMERIC(5,2) | NULL | — | Frame per second |
| `resolution` | TEXT | NULL | — | Enum resolusi |
| `filesize_bytes` | BIGINT | NULL | — | Ukuran file |
| `codec_video` | TEXT | NULL | — | Video codec |
| `codec_audio` | TEXT | NULL | — | Audio codec |
| `bitrate_kbps` | INTEGER | NULL | — | Bitrate total |
| `file_path` | TEXT | NULL | — | Path di Supabase Storage |
| `thumbnail_path` | TEXT | NULL | — | Thumbnail path |
| `status` | TEXT | NOT NULL | 'pending' | Enum status |
| `error_message` | TEXT | NULL | — | Pesan error saat gagal |
| `download_started_at` | TIMESTAMPTZ | NULL | — | Mulai download |
| `download_finished_at` | TIMESTAMPTZ | NULL | — | Selesai download |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | — | Soft delete |

---

### 4.4 `transcripts`

Menyimpan hasil transkripsi Whisper untuk satu video. Satu video maksimal memiliki satu transkrip (1:1).

```sql
CREATE TABLE transcripts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    video_id        UUID        NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID        REFERENCES ai_jobs(id) ON DELETE SET NULL,

    -- Transcript Data
    full_text       TEXT        NOT NULL,            -- Seluruh transkrip dalam satu string
    language        TEXT        NOT NULL,            -- ISO 639-1 (misal: 'en', 'id')
    language_prob   NUMERIC(4,3),                   -- Confidence deteksi bahasa (0.0 - 1.0)

    -- Model Info
    model_used      TEXT        NOT NULL DEFAULT 'base',  -- 'tiny' | 'base' | 'small' | 'medium' | 'large'
    processing_mode TEXT        NOT NULL DEFAULT 'server', -- 'local' | 'server'
    duration_seconds NUMERIC(10,2),                 -- Durasi audio yang diproses

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE transcripts ADD CONSTRAINT uq_transcripts_video UNIQUE (video_id);
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `video_id` | UUID | NOT NULL | — | FK → videos.id CASCADE, UNIQUE |
| `ai_job_id` | UUID | NULL | — | FK → ai_jobs.id |
| `full_text` | TEXT | NOT NULL | — | Teks lengkap |
| `language` | TEXT | NOT NULL | — | ISO 639-1 |
| `language_prob` | NUMERIC(4,3) | NULL | — | 0.000–1.000 |
| `model_used` | TEXT | NOT NULL | 'base' | Whisper model size |
| `processing_mode` | TEXT | NOT NULL | 'server' | Enum: local/server |
| `duration_seconds` | NUMERIC(10,2) | NULL | — | Panjang audio |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |

---

### 4.5 `transcript_words`

Menyimpan setiap kata hasil transkripsi Whisper dengan timestamp-nya. Tabel ini adalah basis Speech Search.

```sql
CREATE TABLE transcript_words (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    transcript_id   UUID            NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,

    -- Word Data
    word            TEXT            NOT NULL,                -- Kata asli
    word_normalized TEXT            NOT NULL,                -- Lowercase, tanpa tanda baca
    start_time      NUMERIC(10,3)   NOT NULL,               -- Detik (presisi milidetik)
    end_time        NUMERIC(10,3)   NOT NULL,               -- Detik
    confidence      NUMERIC(4,3),                           -- 0.000 – 1.000
    segment_index   INTEGER         NOT NULL,               -- Indeks segmen Whisper
    word_index      INTEGER         NOT NULL                -- Posisi kata dalam segmen
);

ALTER TABLE transcript_words ADD CONSTRAINT chk_tw_times
    CHECK (end_time > start_time);

ALTER TABLE transcript_words ADD CONSTRAINT chk_tw_confidence
    CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1));
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `transcript_id` | UUID | NOT NULL | — | FK → transcripts.id CASCADE |
| `word` | TEXT | NOT NULL | — | Kata asli dari Whisper |
| `word_normalized` | TEXT | NOT NULL | — | Untuk indexing full-text search |
| `start_time` | NUMERIC(10,3) | NOT NULL | — | Detik dengan presisi ms |
| `end_time` | NUMERIC(10,3) | NOT NULL | — | Detik dengan presisi ms |
| `confidence` | NUMERIC(4,3) | NULL | — | Confidence Whisper per kata |
| `segment_index` | INTEGER | NOT NULL | — | Nomor segmen Whisper |
| `word_index` | INTEGER | NOT NULL | — | Posisi kata di segmen |

---

### 4.6 `clips`

Menyimpan semua clip yang dihasilkan — baik manual maupun AI-generated.

```sql
CREATE TABLE clips (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id        UUID        NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID        REFERENCES ai_jobs(id) ON DELETE SET NULL,

    -- Clip Identity
    title           TEXT,
    clip_type       TEXT        NOT NULL
                                CHECK (clip_type IN ('manual', 'highlight', 'speech',
                                       'scene', 'object', 'face', 'gesture', 'short')),

    -- Time Range
    start_time      NUMERIC(10,3) NOT NULL CHECK (start_time >= 0),
    end_time        NUMERIC(10,3) NOT NULL CHECK (end_time > start_time),
    duration        NUMERIC(10,3) GENERATED ALWAYS AS (end_time - start_time) STORED,

    -- Output File
    output_path     TEXT,                       -- Supabase Storage path
    thumbnail_path  TEXT,
    filesize_bytes  BIGINT,
    resolution      TEXT        CHECK (resolution IN ('360p', '480p', '720p', '1080p', '1440p', '4k')),
    width           INTEGER,
    height          INTEGER,
    fps             NUMERIC(5,2),

    -- AI Score (untuk highlight clips)
    highlight_score NUMERIC(4,3) CHECK (highlight_score IS NULL OR
                                       (highlight_score >= 0 AND highlight_score <= 1)),

    -- Shorts Metadata
    is_vertical     BOOLEAN     NOT NULL DEFAULT FALSE,  -- TRUE jika 9:16
    has_subtitle    BOOLEAN     NOT NULL DEFAULT FALSE,
    subtitle_path   TEXT,                       -- SRT file path di Storage

    -- Watermark
    has_watermark   BOOLEAN     NOT NULL DEFAULT TRUE,

    -- Status
    status          TEXT        NOT NULL DEFAULT 'processing'
                                CHECK (status IN ('processing', 'ready', 'error', 'deleted')),
    error_message   TEXT,

    -- Metadata tambahan dari AI
    metadata        JSONB,

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ             -- soft delete
);
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `user_id` | UUID | NOT NULL | — | FK → users.id CASCADE |
| `video_id` | UUID | NOT NULL | — | FK → videos.id CASCADE |
| `ai_job_id` | UUID | NULL | — | FK → ai_jobs.id (null jika manual) |
| `title` | TEXT | NULL | — | Judul clip |
| `clip_type` | TEXT | NOT NULL | — | Enum clip_type |
| `start_time` | NUMERIC(10,3) | NOT NULL | — | Detik |
| `end_time` | NUMERIC(10,3) | NOT NULL | — | Detik |
| `duration` | NUMERIC(10,3) | GENERATED | — | end_time - start_time |
| `output_path` | TEXT | NULL | — | Path Supabase Storage |
| `thumbnail_path` | TEXT | NULL | — | Thumbnail path |
| `filesize_bytes` | BIGINT | NULL | — | Ukuran file output |
| `resolution` | TEXT | NULL | — | Enum resolusi |
| `width` | INTEGER | NULL | — | Frame width |
| `height` | INTEGER | NULL | — | Frame height |
| `fps` | NUMERIC(5,2) | NULL | — | FPS output |
| `highlight_score` | NUMERIC(4,3) | NULL | — | 0.000–1.000 |
| `is_vertical` | BOOLEAN | NOT NULL | FALSE | Shorts = TRUE |
| `has_subtitle` | BOOLEAN | NOT NULL | FALSE | Subtitle di-burn |
| `subtitle_path` | TEXT | NULL | — | Path SRT file |
| `has_watermark` | BOOLEAN | NOT NULL | TRUE | Free plan = TRUE |
| `status` | TEXT | NOT NULL | 'processing' | Enum status |
| `error_message` | TEXT | NULL | — | Error detail |
| `metadata` | JSONB | NULL | — | Extra AI metadata |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | — | Soft delete |

---

### 4.7 `ai_jobs`

Menyimpan setiap pekerjaan AI yang dikirim ke Celery worker. Ini adalah pusat tracking semua proses AI.

```sql
CREATE TABLE ai_jobs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id        UUID        NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- Celery Integration
    celery_task_id  TEXT,                       -- Celery task UUID untuk polling
    celery_queue    TEXT,                       -- 'ai_jobs' | 'video_download' | 'export'

    -- Job Config
    job_type        TEXT        NOT NULL
                                CHECK (job_type IN ('highlight', 'speech_search',
                                       'scene_detection', 'object_tracking',
                                       'face_tracking', 'gesture_tracking',
                                       'shorts_generation', 'transcription')),
    status          TEXT        NOT NULL DEFAULT 'queued'
                                CHECK (status IN ('queued', 'processing', 'done', 'failed', 'cancelled')),
    priority        INTEGER     NOT NULL DEFAULT 5
                                CHECK (priority BETWEEN 1 AND 10),
                                -- 1 = premium (highest), 10 = free (lowest)

    -- Input Parameters
    params          JSONB,
    -- Contoh speech_search: {"query": "giveaway", "auto_clip": true, "padding_seconds": 5}
    -- Contoh gesture:       {"gestures": ["wave", "thumbs_up"], "auto_clip": true}
    -- Contoh object:        {"classes": ["person", "car"], "auto_clip": true}

    -- Progress Tracking
    progress        SMALLINT    NOT NULL DEFAULT 0
                                CHECK (progress BETWEEN 0 AND 100),
    progress_message TEXT,                      -- Pesan untuk client: "Analyzing frame 245/3600"

    -- Result Summary
    result_count    INTEGER,                    -- Berapa job_results yang dihasilkan
    error_message   TEXT,
    error_code      TEXT,                       -- Machine-readable error code

    -- Processing Mode
    processing_mode TEXT        NOT NULL DEFAULT 'server'
                                CHECK (processing_mode IN ('local', 'server')),

    -- Timing
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    queued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    finished_at     TIMESTAMPTZ,

    -- GPU Usage (untuk billing/monitoring)
    gpu_seconds_used NUMERIC(10,2) DEFAULT 0,
    model_used      TEXT                        -- 'whisper-base', 'yolov8n', 'mediapipe', dll.
);

ALTER TABLE ai_jobs ADD CONSTRAINT chk_ai_jobs_priority
    CHECK (priority BETWEEN 1 AND 10);

-- Partial unique: satu video tidak boleh punya dua job aktif dengan type yang sama
CREATE UNIQUE INDEX uq_ai_jobs_active_per_video_type
    ON ai_jobs (video_id, job_type)
    WHERE status IN ('queued', 'processing');
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `user_id` | UUID | NOT NULL | — | FK → users.id CASCADE |
| `video_id` | UUID | NOT NULL | — | FK → videos.id CASCADE |
| `celery_task_id` | TEXT | NULL | — | ID task Celery |
| `celery_queue` | TEXT | NULL | — | Queue name |
| `job_type` | TEXT | NOT NULL | — | Enum job_type |
| `status` | TEXT | NOT NULL | 'queued' | Enum job_status |
| `priority` | INTEGER | NOT NULL | 5 | 1=tertinggi, 10=terendah |
| `params` | JSONB | NULL | — | Input parameter |
| `progress` | SMALLINT | NOT NULL | 0 | 0–100 |
| `progress_message` | TEXT | NULL | — | Status teks untuk UI |
| `result_count` | INTEGER | NULL | — | Jumlah hasil |
| `error_message` | TEXT | NULL | — | Pesan error |
| `error_code` | TEXT | NULL | — | Kode error machine-readable |
| `processing_mode` | TEXT | NOT NULL | 'server' | Enum: local/server |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `queued_at` | TIMESTAMPTZ | NOT NULL | NOW() | Masuk queue |
| `started_at` | TIMESTAMPTZ | NULL | — | Mulai diproses worker |
| `finished_at` | TIMESTAMPTZ | NULL | — | Selesai (done/failed) |
| `gpu_seconds_used` | NUMERIC(10,2) | NULL | 0 | Untuk cost tracking |
| `model_used` | TEXT | NULL | — | Model AI yang dipakai |

---

### 4.8 `job_results`

Menyimpan setiap item hasil dari satu AI job. Satu job bisa menghasilkan banyak result (misalnya 10 highlight, 25 scene, dll).

```sql
CREATE TABLE job_results (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    ai_job_id       UUID            NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
    clip_id         UUID            REFERENCES clips(id) ON DELETE SET NULL,

    -- Result Identity
    result_type     TEXT            NOT NULL
                                    CHECK (result_type IN ('highlight', 'speech_match',
                                           'scene', 'object', 'face', 'gesture', 'short')),
    sequence        INTEGER         NOT NULL DEFAULT 1, -- Urutan dalam job (highlight ke-1, ke-2, dst.)

    -- Time Range
    start_time      NUMERIC(10,3),              -- Detik
    end_time        NUMERIC(10,3),              -- Detik
    timestamp_point NUMERIC(10,3),              -- Untuk event point (gesture, object muncul sebentar)

    -- Label & Score
    label           TEXT,                       -- "Hand raised", "Person detected", "Chapter 3"
    score           NUMERIC(4,3)
                    CHECK (score IS NULL OR (score >= 0 AND score <= 1)),

    -- Optional: Speech Match specific
    matched_word    TEXT,                       -- Kata yang dicari (untuk speech_search)
    context_text    TEXT,                       -- Kalimat di sekitar kata

    -- Optional: Object/YOLO specific
    object_class    TEXT,                       -- 'person', 'car', dll.
    bounding_box    JSONB,
    -- Schema: {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4} — normalized 0-1

    -- Optional: Gesture specific
    gesture_type    TEXT,
    pose_landmarks  JSONB,
    -- Schema: array of {x, y, z, visibility} per keypoint (MediaPipe format)

    -- Timestamps
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE job_results ADD CONSTRAINT chk_jr_score
    CHECK (score IS NULL OR (score >= 0 AND score <= 1));
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `ai_job_id` | UUID | NOT NULL | — | FK → ai_jobs.id CASCADE |
| `clip_id` | UUID | NULL | — | FK → clips.id (jika auto-clip) |
| `result_type` | TEXT | NOT NULL | — | Enum result_type |
| `sequence` | INTEGER | NOT NULL | 1 | Urutan hasil |
| `start_time` | NUMERIC(10,3) | NULL | — | Detik mulai |
| `end_time` | NUMERIC(10,3) | NULL | — | Detik selesai |
| `timestamp_point` | NUMERIC(10,3) | NULL | — | Point event (gesture) |
| `label` | TEXT | NULL | — | Label teks |
| `score` | NUMERIC(4,3) | NULL | — | Confidence/skor 0–1 |
| `matched_word` | TEXT | NULL | — | Speech search query |
| `context_text` | TEXT | NULL | — | Kalimat konteks |
| `object_class` | TEXT | NULL | — | YOLO class name |
| `bounding_box` | JSONB | NULL | — | Normalized coords |
| `gesture_type` | TEXT | NULL | — | Enum gesture_type |
| `pose_landmarks` | JSONB | NULL | — | MediaPipe landmarks |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |

---

### 4.9 `scenes`

Menyimpan daftar scene yang terdeteksi dari satu video. Dipisah dari `job_results` karena scene punya struktur data sendiri dan sering di-query secara independen.

```sql
CREATE TABLE scenes (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    video_id        UUID            NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID            REFERENCES ai_jobs(id) ON DELETE SET NULL,
    clip_id         UUID            REFERENCES clips(id) ON DELETE SET NULL,

    -- Scene Data
    scene_index     INTEGER         NOT NULL,           -- Urutan scene (0-based)
    start_time      NUMERIC(10,3)   NOT NULL,
    end_time        NUMERIC(10,3)   NOT NULL,
    duration        NUMERIC(10,3)   GENERATED ALWAYS AS (end_time - start_time) STORED,

    -- Visual Info
    thumbnail_path  TEXT,                               -- Thumbnail frame scene ini
    avg_brightness  NUMERIC(5,2),                       -- Rata-rata brightness (0-255)
    dominant_colors JSONB,
    -- Schema: [{"hex": "#FF5733", "percentage": 0.35}, ...]

    -- Score
    score           NUMERIC(4,3),                       -- Skor "menariknya" scene ini
    is_exported     BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE scenes ADD CONSTRAINT chk_scenes_times
    CHECK (end_time > start_time);

-- Unique: setiap scene index unik per video per job
CREATE UNIQUE INDEX uq_scenes_video_job_index
    ON scenes (video_id, ai_job_id, scene_index);
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `video_id` | UUID | NOT NULL | — | FK → videos.id CASCADE |
| `ai_job_id` | UUID | NULL | — | FK → ai_jobs.id |
| `clip_id` | UUID | NULL | — | FK → clips.id (jika di-export) |
| `scene_index` | INTEGER | NOT NULL | — | 0-based index |
| `start_time` | NUMERIC(10,3) | NOT NULL | — | Detik |
| `end_time` | NUMERIC(10,3) | NOT NULL | — | Detik |
| `duration` | NUMERIC(10,3) | GENERATED | — | end - start |
| `thumbnail_path` | TEXT | NULL | — | Preview thumbnail |
| `avg_brightness` | NUMERIC(5,2) | NULL | — | 0–255 |
| `dominant_colors` | JSONB | NULL | — | Array warna dominan |
| `score` | NUMERIC(4,3) | NULL | — | Skor scene |
| `is_exported` | BOOLEAN | NOT NULL | FALSE | Sudah jadi clip? |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |

---

### 4.10 `object_detections`

Menyimpan event deteksi objek dari YOLOv8. Setiap row = satu kemunculan objek tertentu dalam rentang waktu.

```sql
CREATE TABLE object_detections (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    video_id        UUID            NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID            NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
    clip_id         UUID            REFERENCES clips(id) ON DELETE SET NULL,

    -- Detection Data
    class_name      TEXT            NOT NULL
                                    CHECK (class_name IN ('person', 'car', 'motorcycle',
                                           'cat', 'dog', 'bicycle', 'bus', 'truck')),
    track_id        INTEGER,                    -- YOLO tracking ID (konsisten antar frame)

    -- Time Range (kemunculan objek ini)
    start_time      NUMERIC(10,3)   NOT NULL,
    end_time        NUMERIC(10,3)   NOT NULL,
    peak_time       NUMERIC(10,3),              -- Timestamp confidence tertinggi

    -- Confidence
    avg_confidence  NUMERIC(4,3)    NOT NULL,
    max_confidence  NUMERIC(4,3),

    -- Spatial (pada frame peak_time)
    bounding_box    JSONB,
    -- Schema: {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4}

    -- Timestamps
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

---

### 4.11 `face_detections`

Menyimpan event deteksi wajah dari MediaPipe. Setiap row = satu wajah yang di-track selama rentang waktu tertentu.

```sql
CREATE TABLE face_detections (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    video_id        UUID            NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID            NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
    clip_id         UUID            REFERENCES clips(id) ON DELETE SET NULL,

    -- Face Track Data
    face_track_id   INTEGER         NOT NULL,   -- ID wajah konsisten antar frame (0, 1, 2...)

    -- Time Range
    start_time      NUMERIC(10,3)   NOT NULL,
    end_time        NUMERIC(10,3)   NOT NULL,
    total_frames    INTEGER,                    -- Jumlah frame wajah terdeteksi

    -- Quality Metrics
    avg_confidence  NUMERIC(4,3),
    avg_face_size   NUMERIC(6,4),               -- Rata-rata ukuran wajah (0–1, rel. frame)
    is_front_facing BOOLEAN,                    -- TRUE jika rata-rata menghadap kamera

    -- Spatial (frame representatif)
    bounding_box    JSONB,

    -- Face Landmarks (titik-titik pada frame representatif)
    landmarks       JSONB,
    -- Schema: {"left_eye": [x,y], "right_eye": [x,y], "nose": [x,y],
    --          "mouth_left": [x,y], "mouth_right": [x,y]}

    -- Timestamps
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

---

### 4.12 `gesture_detections`

Menyimpan event deteksi gesture dari MediaPipe + YOLO Pose. Setiap row = satu kejadian gesture pada timestamp tertentu.

```sql
CREATE TABLE gesture_detections (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    video_id        UUID            NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID            NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
    clip_id         UUID            REFERENCES clips(id) ON DELETE SET NULL,

    -- Gesture Data
    gesture_type    TEXT            NOT NULL
                                    CHECK (gesture_type IN ('pointing', 'hand_raised',
                                           'wave', 'thumbs_up', 'clap', 'facing_camera')),
    direction       TEXT,                       -- 'left' | 'right' | 'up' | 'down' (untuk pointing)

    -- Timestamp (event point, bukan rentang)
    timestamp       NUMERIC(10,3)   NOT NULL,
    duration_seconds NUMERIC(6,2),              -- Berapa lama gesture berlangsung

    -- Confidence
    confidence      NUMERIC(4,3)    NOT NULL,

    -- Pose Data
    pose_landmarks  JSONB,
    -- Schema: array 33 keypoints MediaPipe BlazePose
    -- [{"x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.99}, ...]

    -- Clip Range
    clip_start_time NUMERIC(10,3),              -- start_time yang akan di-clip (timestamp - padding)
    clip_end_time   NUMERIC(10,3),              -- end_time yang akan di-clip

    -- Timestamps
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

---

### 4.13 `highlights`

Menyimpan highlight yang dihasilkan oleh AI Highlight Detection. Ini adalah tabel terstruktur (bukan JSONB) untuk query ranking yang efisien.

```sql
CREATE TABLE highlights (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    video_id        UUID            NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID            NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
    clip_id         UUID            REFERENCES clips(id) ON DELETE SET NULL,

    -- Highlight Range
    start_time      NUMERIC(10,3)   NOT NULL,
    end_time        NUMERIC(10,3)   NOT NULL,
    duration        NUMERIC(10,3)   GENERATED ALWAYS AS (end_time - start_time) STORED,
    rank            INTEGER         NOT NULL,   -- 1 = highlight terbaik

    -- Composite Score (0.0 - 1.0)
    total_score         NUMERIC(4,3)    NOT NULL,

    -- Score Breakdown
    audio_energy_score  NUMERIC(4,3),           -- 35% bobot
    transcript_score    NUMERIC(4,3),           -- 25% bobot (keyword/emotion density)
    scene_change_score  NUMERIC(4,3),           -- 20% bobot
    visual_activity_score NUMERIC(4,3),         -- 20% bobot (motion vector)

    -- Supporting Data
    peak_audio_db       NUMERIC(6,2),           -- dB audio tertinggi dalam segment
    keyword_hits        JSONB,
    -- Schema: [{"word": "giveaway", "timestamp": 12.5}, ...]

    -- Timestamps
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE highlights ADD CONSTRAINT chk_highlights_times
    CHECK (end_time > start_time);

ALTER TABLE highlights ADD CONSTRAINT chk_highlights_score
    CHECK (total_score BETWEEN 0 AND 1);
```

---

### 4.14 `payments`

Menyimpan riwayat transaksi pembayaran dari Google Play dan Stripe.

```sql
CREATE TABLE payments (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    subscription_id     UUID        REFERENCES subscriptions(id) ON DELETE SET NULL,

    -- Amount
    amount              NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    currency            TEXT        NOT NULL DEFAULT 'USD',   -- ISO 4217
    amount_usd          NUMERIC(12,2),                       -- Normalized ke USD

    -- Provider
    provider            TEXT        NOT NULL
                                    CHECK (provider IN ('google_play', 'stripe', 'manual')),
    provider_tx_id      TEXT,                   -- Transaction ID dari provider
    provider_order_id   TEXT,                   -- Order ID
    provider_product_id TEXT,                   -- SKU / Product ID
    provider_raw        JSONB,                  -- Raw webhook payload

    -- Status
    status              TEXT        NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending', 'success', 'failed',
                                           'refunded', 'disputed')),
    failure_reason      TEXT,

    -- Timestamps
    paid_at             TIMESTAMPTZ,            -- Waktu pembayaran berhasil
    refunded_at         TIMESTAMPTZ,            -- Waktu refund (jika ada)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Idempotency: jangan simpan transaksi yang sama dua kali
CREATE UNIQUE INDEX uq_payments_provider_tx
    ON payments (provider, provider_tx_id)
    WHERE provider_tx_id IS NOT NULL;
```

**Kolom Detail:**

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | UUID | NOT NULL | gen_random_uuid() | PK |
| `user_id` | UUID | NOT NULL | — | FK → users.id RESTRICT |
| `subscription_id` | UUID | NULL | — | FK → subscriptions.id |
| `amount` | NUMERIC(12,2) | NOT NULL | — | Nominal transaksi |
| `currency` | TEXT | NOT NULL | 'USD' | ISO 4217 |
| `amount_usd` | NUMERIC(12,2) | NULL | — | Normalize ke USD |
| `provider` | TEXT | NOT NULL | — | Enum provider |
| `provider_tx_id` | TEXT | NULL | — | UNIQUE per provider |
| `provider_order_id` | TEXT | NULL | — | Order reference |
| `provider_product_id` | TEXT | NULL | — | SKU |
| `provider_raw` | JSONB | NULL | — | Raw webhook |
| `status` | TEXT | NOT NULL | 'pending' | Enum payment_status |
| `failure_reason` | TEXT | NULL | — | Error dari provider |
| `paid_at` | TIMESTAMPTZ | NULL | — | Waktu sukses |
| `refunded_at` | TIMESTAMPTZ | NULL | — | Waktu refund |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | |

---

### 4.15 `usage_logs`

Tabel audit semua aktivitas user untuk keperluan quota enforcement, analytics, dan billing.

```sql
CREATE TABLE usage_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id        UUID        REFERENCES videos(id) ON DELETE SET NULL,
    clip_id         UUID        REFERENCES clips(id) ON DELETE SET NULL,
    ai_job_id       UUID        REFERENCES ai_jobs(id) ON DELETE SET NULL,

    -- Action
    action          TEXT        NOT NULL
                                CHECK (action IN ('video_import', 'clip_export',
                                       'ai_job_submit', 'storage_upload')),

    -- Quota Tracking
    date            DATE        NOT NULL DEFAULT CURRENT_DATE,  -- untuk daily quota check

    -- Resource Consumption
    duration_seconds INTEGER,               -- Durasi video yang diproses (untuk quota)
    filesize_bytes  BIGINT,                 -- Size upload/download

    -- Context
    plan_at_time    TEXT,                   -- Plan user saat aksi dilakukan (snapshot)
    ip_address      INET,                   -- IP client
    user_agent      TEXT,

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 4.16 `api_keys`

Menyimpan API key untuk akses programatik (Phase 4 — Public API).

```sql
CREATE TABLE api_keys (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Key Data
    name            TEXT        NOT NULL,            -- Label dari user: "My App Key"
    key_prefix      TEXT        NOT NULL,            -- 8 karakter awal untuk display: "cfk_xxxx"
    key_hash        TEXT        NOT NULL,            -- bcrypt hash dari full key
    key_last4       TEXT        NOT NULL,            -- 4 karakter akhir untuk display

    -- Permissions
    scopes          TEXT[]      NOT NULL DEFAULT '{read}',
    -- Nilai: 'read', 'write', 'admin'

    -- Rate Limit
    rate_limit_rpm  INTEGER     NOT NULL DEFAULT 60, -- Request per menit

    -- Status
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,                     -- NULL = tidak expired

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ
);

CREATE UNIQUE INDEX uq_api_keys_prefix ON api_keys (key_prefix);
CREATE UNIQUE INDEX uq_api_keys_hash ON api_keys (key_hash);
```

---

### 4.17 `notifications`

Menyimpan notifikasi in-app untuk user (job selesai, subscription expiring, dll).

```sql
CREATE TABLE notifications (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ai_job_id       UUID        REFERENCES ai_jobs(id) ON DELETE SET NULL,

    -- Notification Data
    type            TEXT        NOT NULL
                                CHECK (type IN ('job_done', 'job_failed',
                                       'subscription_expiring', 'subscription_expired',
                                       'new_feature', 'system')),
    title           TEXT        NOT NULL,
    body            TEXT        NOT NULL,
    action_url      TEXT,                       -- Deep link (misal: /clips/{id})
    data            JSONB,                      -- Extra payload (job_id, clip_id, dll)

    -- Status
    is_read         BOOLEAN     NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMPTZ,

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ                 -- NULL = tidak expired
);
```

---

## 5. Indexes

Semua index dirancang berdasarkan query pattern yang paling sering dijalankan.

```sql
-- ══════════════════════════════════════════════
-- users
-- ══════════════════════════════════════════════
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_plan ON users (plan) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_is_admin ON users (is_admin) WHERE is_admin = TRUE;

-- ══════════════════════════════════════════════
-- subscriptions
-- ══════════════════════════════════════════════
CREATE INDEX idx_subscriptions_user_id ON subscriptions (user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions (status);
CREATE INDEX idx_subscriptions_expires ON subscriptions (expires_at)
    WHERE status = 'active';     -- Untuk cron job reminder expiring

-- ══════════════════════════════════════════════
-- videos
-- ══════════════════════════════════════════════
CREATE INDEX idx_videos_user_id ON videos (user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_videos_status ON videos (status);
CREATE INDEX idx_videos_youtube_id ON videos (youtube_id);
CREATE INDEX idx_videos_created_at ON videos (user_id, created_at DESC)
    WHERE deleted_at IS NULL;    -- List video user terbaru

-- ══════════════════════════════════════════════
-- transcripts
-- ══════════════════════════════════════════════
CREATE INDEX idx_transcripts_video_id ON transcripts (video_id);

-- Full-text search pada transcript keseluruhan
CREATE INDEX idx_transcripts_fulltext ON transcripts
    USING GIN (to_tsvector('english', full_text));

-- ══════════════════════════════════════════════
-- transcript_words
-- ══════════════════════════════════════════════
CREATE INDEX idx_tw_transcript_id ON transcript_words (transcript_id);
CREATE INDEX idx_tw_word_normalized ON transcript_words (word_normalized);

-- Index untuk speech search: cari kata dalam transcript tertentu
CREATE INDEX idx_tw_transcript_word ON transcript_words (transcript_id, word_normalized);

-- ══════════════════════════════════════════════
-- clips
-- ══════════════════════════════════════════════
CREATE INDEX idx_clips_user_id ON clips (user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_clips_video_id ON clips (video_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_clips_ai_job_id ON clips (ai_job_id);
CREATE INDEX idx_clips_type ON clips (clip_type);
CREATE INDEX idx_clips_created_at ON clips (user_id, created_at DESC)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_clips_highlight_score ON clips (highlight_score DESC)
    WHERE clip_type = 'highlight' AND deleted_at IS NULL;

-- ══════════════════════════════════════════════
-- ai_jobs
-- ══════════════════════════════════════════════
CREATE INDEX idx_ai_jobs_user_id ON ai_jobs (user_id);
CREATE INDEX idx_ai_jobs_video_id ON ai_jobs (video_id);
CREATE INDEX idx_ai_jobs_status ON ai_jobs (status);
CREATE INDEX idx_ai_jobs_celery_task_id ON ai_jobs (celery_task_id)
    WHERE celery_task_id IS NOT NULL;
CREATE INDEX idx_ai_jobs_priority_queued ON ai_jobs (priority ASC, created_at ASC)
    WHERE status = 'queued';     -- Admin queue monitor, Celery pick-up order
CREATE INDEX idx_ai_jobs_user_active ON ai_jobs (user_id, status)
    WHERE status IN ('queued', 'processing');

-- ══════════════════════════════════════════════
-- job_results
-- ══════════════════════════════════════════════
CREATE INDEX idx_jr_ai_job_id ON job_results (ai_job_id);
CREATE INDEX idx_jr_clip_id ON job_results (clip_id);
CREATE INDEX idx_jr_type ON job_results (result_type);

-- ══════════════════════════════════════════════
-- scenes
-- ══════════════════════════════════════════════
CREATE INDEX idx_scenes_video_id ON scenes (video_id);
CREATE INDEX idx_scenes_ai_job_id ON scenes (ai_job_id);

-- ══════════════════════════════════════════════
-- object_detections
-- ══════════════════════════════════════════════
CREATE INDEX idx_od_video_id ON object_detections (video_id);
CREATE INDEX idx_od_ai_job_id ON object_detections (ai_job_id);
CREATE INDEX idx_od_class ON object_detections (class_name);
CREATE INDEX idx_od_video_class ON object_detections (video_id, class_name);

-- ══════════════════════════════════════════════
-- face_detections
-- ══════════════════════════════════════════════
CREATE INDEX idx_fd_video_id ON face_detections (video_id);
CREATE INDEX idx_fd_ai_job_id ON face_detections (ai_job_id);

-- ══════════════════════════════════════════════
-- gesture_detections
-- ══════════════════════════════════════════════
CREATE INDEX idx_gd_video_id ON gesture_detections (video_id);
CREATE INDEX idx_gd_ai_job_id ON gesture_detections (ai_job_id);
CREATE INDEX idx_gd_type ON gesture_detections (gesture_type);
CREATE INDEX idx_gd_video_type ON gesture_detections (video_id, gesture_type);

-- ══════════════════════════════════════════════
-- highlights
-- ══════════════════════════════════════════════
CREATE INDEX idx_hl_video_id ON highlights (video_id);
CREATE INDEX idx_hl_ai_job_id ON highlights (ai_job_id);
CREATE INDEX idx_hl_rank ON highlights (ai_job_id, rank ASC);
CREATE INDEX idx_hl_score ON highlights (total_score DESC);

-- ══════════════════════════════════════════════
-- payments
-- ══════════════════════════════════════════════
CREATE INDEX idx_payments_user_id ON payments (user_id);
CREATE INDEX idx_payments_status ON payments (status);
CREATE INDEX idx_payments_created_at ON payments (created_at DESC);

-- ══════════════════════════════════════════════
-- usage_logs
-- ══════════════════════════════════════════════
-- Kritis: dipakai setiap request untuk quota check
CREATE INDEX idx_usage_user_date ON usage_logs (user_id, date);
CREATE INDEX idx_usage_user_action_date ON usage_logs (user_id, action, date);
CREATE INDEX idx_usage_date ON usage_logs (date);   -- Admin stats harian

-- ══════════════════════════════════════════════
-- notifications
-- ══════════════════════════════════════════════
CREATE INDEX idx_notif_user_unread ON notifications (user_id, created_at DESC)
    WHERE is_read = FALSE;
CREATE INDEX idx_notif_user_id ON notifications (user_id);
```

---

## 6. Constraints & Business Rules

### 6.1 Check Constraints Ringkasan

| Tabel | Constraint | Rule |
|---|---|---|
| `users` | `chk_users_storage` | `storage_used_bytes >= 0` |
| `subscriptions` | `uq_subscriptions_active_per_user` | Partial unique: hanya 1 active per user |
| `videos` | `uq_videos_user_youtube` | Partial unique: (user_id, youtube_id) WHERE deleted_at IS NULL |
| `clips` | `chk_clips_times` | `end_time > start_time` |
| `clips` | `chk_clips_score` | `highlight_score BETWEEN 0 AND 1` |
| `ai_jobs` | `chk_ai_jobs_priority` | `priority BETWEEN 1 AND 10` |
| `ai_jobs` | `uq_ai_jobs_active` | Partial unique: tidak ada 2 job aktif (type+video) |
| `job_results` | `chk_jr_score` | `score BETWEEN 0 AND 1` |
| `scenes` | `chk_scenes_times` | `end_time > start_time` |
| `highlights` | `chk_highlights_times` | `end_time > start_time` |
| `highlights` | `chk_highlights_score` | `total_score BETWEEN 0 AND 1` |
| `payments` | `uq_payments_provider_tx` | Partial unique: idempotency per provider_tx_id |

### 6.2 Trigger: Auto-update `updated_at`

```sql
-- Fungsi reusable untuk semua tabel
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply ke semua tabel yang punya updated_at
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_clips_updated_at
    BEFORE UPDATE ON clips
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_ai_jobs_updated_at
    BEFORE UPDATE ON ai_jobs
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
```

### 6.3 Trigger: Sync `users.plan` dari `subscriptions`

```sql
-- Setiap kali status subscription berubah, sync plan ke users
CREATE OR REPLACE FUNCTION sync_user_plan_from_subscription()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'active' THEN
        UPDATE users SET plan = NEW.plan, updated_at = NOW()
        WHERE id = NEW.user_id;
    ELSIF NEW.status IN ('expired', 'cancelled') THEN
        -- Cek apakah masih ada active subscription lain
        IF NOT EXISTS (
            SELECT 1 FROM subscriptions
            WHERE user_id = NEW.user_id AND status = 'active' AND id != NEW.id
        ) THEN
            UPDATE users SET plan = 'free', updated_at = NOW()
            WHERE id = NEW.user_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_user_plan
    AFTER INSERT OR UPDATE OF status ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION sync_user_plan_from_subscription();
```

### 6.4 Trigger: Update `storage_used_bytes` di `users`

```sql
-- Saat clip baru selesai (output_path di-set), tambah storage usage
CREATE OR REPLACE FUNCTION update_user_storage_on_clip()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.filesize_bytes IS NOT NULL AND OLD.filesize_bytes IS DISTINCT FROM NEW.filesize_bytes THEN
        UPDATE users
        SET storage_used_bytes = storage_used_bytes
                                 + COALESCE(NEW.filesize_bytes, 0)
                                 - COALESCE(OLD.filesize_bytes, 0)
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_clips_storage
    AFTER UPDATE OF filesize_bytes ON clips
    FOR EACH ROW EXECUTE FUNCTION update_user_storage_on_clip();
```

---

## 7. JSONB Column Schemas

Kolom JSONB memiliki schema yang tidak di-enforce oleh DB, tapi harus divalidasi di application layer (Pydantic).

### `ai_jobs.params`

**speech_search:**
```json
{
  "query": "giveaway",
  "auto_clip": true,
  "padding_seconds": 5,
  "min_confidence": 0.7
}
```

**object_tracking:**
```json
{
  "classes": ["person", "car", "cat"],
  "auto_clip": true,
  "padding_seconds": 3,
  "min_confidence": 0.5,
  "min_duration_seconds": 2.0
}
```

**gesture_tracking:**
```json
{
  "gestures": ["thumbs_up", "hand_raised", "wave"],
  "auto_clip": true,
  "padding_seconds": 3
}
```

**shorts_generation:**
```json
{
  "source_clip_id": "uuid",
  "aspect_ratio": "9:16",
  "auto_subtitle": true,
  "subtitle_font": "default",
  "auto_center": true,
  "auto_zoom": true
}
```

---

### `job_results.bounding_box`

Koordinat dinormalisasi 0.0–1.0 relatif terhadap ukuran frame:
```json
{
  "x": 0.12,
  "y": 0.08,
  "w": 0.35,
  "h": 0.65
}
```

---

### `job_results.pose_landmarks`

33 keypoint MediaPipe BlazePose:
```json
[
  {"name": "nose", "x": 0.50, "y": 0.22, "z": -0.10, "visibility": 0.99},
  {"name": "left_eye", "x": 0.53, "y": 0.20, "z": -0.11, "visibility": 0.98},
  {"name": "right_eye", "x": 0.47, "y": 0.20, "z": -0.11, "visibility": 0.97},
  {"name": "left_wrist", "x": 0.65, "y": 0.55, "z": -0.05, "visibility": 0.95},
  {"name": "right_wrist", "x": 0.35, "y": 0.30, "z": -0.08, "visibility": 0.92}
]
```

---

### `scenes.dominant_colors`

```json
[
  {"hex": "#1A2B3C", "percentage": 0.45},
  {"hex": "#FFFFFF", "percentage": 0.30},
  {"hex": "#FF5733", "percentage": 0.25}
]
```

---

### `subscriptions.provider_data`

**Google Play:**
```json
{
  "orderId": "GPA.xxxx",
  "packageName": "com.clipforge.app",
  "productId": "premium_monthly",
  "purchaseTime": 1748700000000,
  "purchaseState": 0,
  "purchaseToken": "xxxx"
}
```

**Stripe:**
```json
{
  "id": "sub_xxxx",
  "object": "subscription",
  "customer": "cus_xxxx",
  "status": "active",
  "current_period_end": 1751292000
}
```

---

## 8. Relationships Summary

| Tabel Parent | Tabel Child | Cardinality | FK | On Delete |
|---|---|---|---|---|
| `users` | `subscriptions` | 1:N | `user_id` | CASCADE |
| `users` | `videos` | 1:N | `user_id` | CASCADE |
| `users` | `clips` | 1:N | `user_id` | CASCADE |
| `users` | `ai_jobs` | 1:N | `user_id` | CASCADE |
| `users` | `payments` | 1:N | `user_id` | RESTRICT |
| `users` | `usage_logs` | 1:N | `user_id` | CASCADE |
| `users` | `api_keys` | 1:N | `user_id` | CASCADE |
| `users` | `notifications` | 1:N | `user_id` | CASCADE |
| `subscriptions` | `payments` | 1:N | `subscription_id` | SET NULL |
| `videos` | `transcripts` | 1:1 | `video_id` | CASCADE |
| `videos` | `clips` | 1:N | `video_id` | CASCADE |
| `videos` | `ai_jobs` | 1:N | `video_id` | CASCADE |
| `videos` | `scenes` | 1:N | `video_id` | CASCADE |
| `videos` | `object_detections` | 1:N | `video_id` | CASCADE |
| `videos` | `face_detections` | 1:N | `video_id` | CASCADE |
| `videos` | `gesture_detections` | 1:N | `video_id` | CASCADE |
| `videos` | `highlights` | 1:N | `video_id` | CASCADE |
| `transcripts` | `transcript_words` | 1:N | `transcript_id` | CASCADE |
| `ai_jobs` | `job_results` | 1:N | `ai_job_id` | CASCADE |
| `ai_jobs` | `scenes` | 1:N | `ai_job_id` | SET NULL |
| `ai_jobs` | `object_detections` | 1:N | `ai_job_id` | CASCADE |
| `ai_jobs` | `face_detections` | 1:N | `ai_job_id` | CASCADE |
| `ai_jobs` | `gesture_detections` | 1:N | `ai_job_id` | CASCADE |
| `ai_jobs` | `highlights` | 1:N | `ai_job_id` | CASCADE |
| `clips` | `job_results` | 1:N | `clip_id` | SET NULL |
| `clips` | `scenes` | 1:N | `clip_id` | SET NULL |
| `clips` | `object_detections` | 1:N | `clip_id` | SET NULL |
| `clips` | `face_detections` | 1:N | `clip_id` | SET NULL |
| `clips` | `gesture_detections` | 1:N | `clip_id` | SET NULL |
| `clips` | `highlights` | 1:N | `clip_id` | SET NULL |

---

## 9. Common Queries

### Cek Quota Harian User (Free Plan)

```sql
-- Berapa kali user import video hari ini?
SELECT COUNT(*) AS import_count
FROM usage_logs
WHERE user_id = $1
  AND action = 'video_import'
  AND date = CURRENT_DATE;
-- Index: idx_usage_user_action_date
```

### Speech Search — Cari Timestamp Kata

```sql
-- Cari semua kemunculan kata "giveaway" dalam video tertentu
SELECT
    tw.word,
    tw.start_time,
    tw.end_time,
    tw.confidence
FROM transcript_words tw
JOIN transcripts t ON tw.transcript_id = t.id
WHERE t.video_id = $1
  AND tw.word_normalized = LOWER($2)
ORDER BY tw.start_time ASC;
-- Index: idx_tw_transcript_word
```

### List Top Highlights untuk Satu Job

```sql
-- Ambil 5 highlight terbaik dari satu job
SELECT
    h.start_time,
    h.end_time,
    h.duration,
    h.rank,
    h.total_score,
    h.audio_energy_score,
    h.transcript_score,
    c.output_path,
    c.thumbnail_path
FROM highlights h
LEFT JOIN clips c ON h.clip_id = c.id
WHERE h.ai_job_id = $1
ORDER BY h.rank ASC
LIMIT 5;
-- Index: idx_hl_rank
```

### List Gesture Events dari Satu Video

```sql
-- Semua gesture dalam satu video, sorted by timestamp
SELECT
    gd.gesture_type,
    gd.direction,
    gd.timestamp,
    gd.duration_seconds,
    gd.confidence,
    gd.clip_start_time,
    gd.clip_end_time,
    c.output_path
FROM gesture_detections gd
LEFT JOIN clips c ON gd.clip_id = c.id
WHERE gd.video_id = $1
  AND gd.gesture_type = ANY($2::TEXT[])   -- filter gesture tertentu
ORDER BY gd.timestamp ASC;
-- Index: idx_gd_video_type
```

### Admin: Statistik Harian

```sql
-- Ringkasan aktivitas per hari (untuk admin dashboard)
SELECT
    date,
    COUNT(*) FILTER (WHERE action = 'video_import')   AS videos_imported,
    COUNT(*) FILTER (WHERE action = 'clip_export')    AS clips_exported,
    COUNT(*) FILTER (WHERE action = 'ai_job_submit')  AS ai_jobs_submitted
FROM usage_logs
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date
ORDER BY date DESC;
-- Index: idx_usage_date
```

### Cek Active Subscription User

```sql
SELECT
    s.plan,
    s.status,
    s.started_at,
    s.expires_at,
    s.payment_provider,
    s.provider_product_id,
    CASE
        WHEN s.expires_at IS NULL THEN TRUE
        WHEN s.expires_at > NOW() THEN TRUE
        ELSE FALSE
    END AS is_valid
FROM subscriptions s
WHERE s.user_id = $1
  AND s.status = 'active'
LIMIT 1;
-- Index: uq_subscriptions_active_per_user
```

### Job Queue Monitor (Admin)

```sql
-- Status queue real-time
SELECT
    job_type,
    status,
    priority,
    COUNT(*) AS job_count,
    AVG(EXTRACT(EPOCH FROM (NOW() - queued_at))) AS avg_wait_seconds
FROM ai_jobs
WHERE status IN ('queued', 'processing')
GROUP BY job_type, status, priority
ORDER BY priority ASC, job_type;
-- Index: idx_ai_jobs_priority_queued
```

### User Storage Usage

```sql
-- Berapa total storage yang dipakai user
SELECT
    u.id,
    u.email,
    u.plan,
    u.storage_used_bytes,
    u.storage_quota_bytes,
    ROUND(u.storage_used_bytes::NUMERIC / u.storage_quota_bytes * 100, 2) AS usage_pct
FROM users u
WHERE u.id = $1;
```

---

## 10. Migration Strategy

Semua perubahan schema dikelola via **Alembic** dengan konvensi penamaan file:

```
db/migrations/versions/
├── 0001_initial_schema.py          -- Semua tabel dasar
├── 0002_add_transcripts.py         -- transcripts + transcript_words
├── 0003_add_ai_detection_tables.py -- scenes, object_, face_, gesture_detections
├── 0004_add_highlights.py          -- highlights
├── 0005_add_notifications.py       -- notifications
├── 0006_add_api_keys.py            -- api_keys
└── 0007_add_storage_tracking.py    -- storage_used_bytes di users
```

### Aturan Migration

| Aturan | Detail |
|---|---|
| **Selalu backward compatible** | Tambah kolom dengan DEFAULT atau NULLABLE |
| **Tidak drop kolom langsung** | Rename → deprecated → drop di migration berikutnya |
| **Index concurrently** | Gunakan `CREATE INDEX CONCURRENTLY` di production |
| **Zero-downtime** | Setiap migration harus bisa dijalankan tanpa stop server |
| **Rollback wajib** | Setiap file migration harus memiliki fungsi `downgrade()` |

### Contoh Alembic Migration File

```python
# 0001_initial_schema.py

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('supabase_uid', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('plan', sa.Text(), nullable=False, server_default='free'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supabase_uid'),
        sa.UniqueConstraint('email'),
        sa.CheckConstraint("plan IN ('free', 'premium')", name='chk_users_plan')
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

---

*ClipForge Database Schema v1.0.0*
*Dokumen ini adalah sumber kebenaran tunggal (single source of truth) untuk semua struktur data ClipForge.*
*Update bersama dengan setiap Alembic migration.*
