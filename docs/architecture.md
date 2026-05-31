# ClipForge — System Architecture Document

**Version:** 1.0.0
**Last Updated:** 2026-05-31
**Status:** Ready for Development

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack & Rationale](#2-technology-stack--rationale)
3. [High-Level Architecture](#3-high-level-architecture)
4. [Project Folder Structure](#4-project-folder-structure)
5. [Database Schema](#5-database-schema)
6. [API Specification](#6-api-specification)
7. [AI Pipeline Architecture](#7-ai-pipeline-architecture)
8. [Android Architecture](#8-android-architecture)
9. [UI/UX Flow](#9-uiux-flow)
10. [Subscription & Entitlement System](#10-subscription--entitlement-system)
11. [Queue & Job System](#11-queue--job-system)
12. [Admin Panel Architecture](#12-admin-panel-architecture)
13. [Infrastructure & Deployment](#13-infrastructure--deployment)
14. [Environment Variables](#14-environment-variables)
15. [Security Architecture](#15-security-architecture)
16. [Roadmap: MVP to Production](#16-roadmap-mvp-to-production)

---

## 1. System Overview

ClipForge adalah aplikasi **AI Video Clipper** berbasis Android yang memungkinkan pengguna memotong, mendeteksi, dan menganalisis video YouTube secara otomatis menggunakan kecerdasan buatan.

### 1.1 Core Value Proposition

| Dimensi | Deskripsi |
|---|---|
| **Target User** | Content creator, editor video, social media manager |
| **Problem** | Proses klip video manual lambat dan tidak scalable |
| **Solution** | AI otomatis mendeteksi momen terbaik, wajah, gesture, objek, dan ucapan |
| **Monetization** | Freemium — Free Plan (terbatas) → Premium Plan (unlimited) |

### 1.2 Processing Modes

ClipForge mendukung dua mode pemrosesan yang dapat dipilih pengguna saat onboarding:

```
┌─────────────────────────────────────────────────────────┐
│                   AI Processing Mode                    │
├──────────────────────────┬──────────────────────────────┤
│       LOCAL AI           │         SERVER AI            │
│  • On-device inference   │  • GPU server processing     │
│  • Privacy-first         │  • Faster & more accurate    │
│  • No upload needed      │  • Supports 4K & long video  │
│  • Uses device RAM       │  • Requires internet          │
└──────────────────────────┴──────────────────────────────┘
```

---

## 2. Technology Stack & Rationale

### 2.1 Android (Client)

| Teknologi | Versi | Alasan Pemilihan |
|---|---|---|
| **Kotlin** | 2.x | First-class Android language, null-safety, coroutines |
| **Jetpack Compose** | Latest Stable | Declarative UI, lebih mudah maintain, animasi modern |
| **Material 3** | Latest | Desain konsisten, theming dinamis |
| **Hilt** | 2.x | DI framework resmi Google, terintegrasi dengan Compose |
| **Retrofit + OkHttp** | Latest | HTTP client yang mature dan reliable |
| **Coil** | Latest | Image loading ringan, Compose-native |
| **ExoPlayer / Media3** | Latest | Video playback premium, thumbnail extraction |
| **DataStore** | Latest | Menggantikan SharedPreferences, type-safe |
| **Room** | Latest | Local DB untuk cache clips & metadata |
| **WorkManager** | Latest | Background task untuk download & local AI inference |
| **TFLite / ONNX Runtime** | Latest | Local AI inference untuk mode Local AI |
| **Supabase Android SDK** | Latest | Auth management terintegrasi |

### 2.2 Backend

| Teknologi | Versi | Alasan Pemilihan |
|---|---|---|
| **Python** | 3.12+ | Ekosistem AI/ML terbaik |
| **FastAPI** | 0.11x | Async-native, auto OpenAPI docs, performa tinggi |
| **PostgreSQL** | 16 | ACID-compliant, JSON support, battle-tested |
| **Redis** | 7.x | Job queue (Celery broker) & caching layer |
| **SQLAlchemy** | 2.x | ORM async-ready, mendukung PostgreSQL penuh |
| **Alembic** | Latest | Database migration management |
| **Celery** | 5.x | Distributed task queue untuk AI jobs |
| **Supabase** | Latest | Auth + Realtime + Storage |

### 2.3 AI / ML Stack

| Teknologi | Fungsi |
|---|---|
| **yt-dlp** | Download video & ekstraksi metadata YouTube |
| **FFmpeg** | Video cutting, transcoding, watermark, crop |
| **Whisper (OpenAI)** | Speech-to-text untuk transkrip & speech search |
| **YOLOv8** | Object detection (person, car, cat, dog, dll.) |
| **YOLO Pose** | Pose estimation untuk gesture detection |
| **MediaPipe** | Face tracking & gesture landmark detection |
| **PySceneDetect** | Scene change detection otomatis |

### 2.4 Infrastructure

| Teknologi | Alasan |
|---|---|
| **Docker + Docker Compose** | Reproducible environment, mudah deploy |
| **Nginx** | Reverse proxy, SSL termination, rate limiting |
| **Supabase Storage** | Object storage untuk video & clip output |
| **GitHub Actions** | CI/CD pipeline |
| **Flower** | Celery monitoring dashboard |

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ANDROID CLIENT                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Auth UI │  │ Dashboard│  │ AI Clips │  │  Settings/Subs   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       └─────────────┴─────────────┴─────────────────┘             │
│                          ViewModel Layer (Hilt)                    │
│                     Repository → DataSource Layer                  │
│              ┌───────────────────┬────────────────────┐            │
│              │  Retrofit (REST)  │  Room (Local Cache) │            │
│              └────────┬──────────┴────────────────────┘            │
└───────────────────────┼─────────────────────────────────────────────┘
                        │ HTTPS / JWT
┌───────────────────────▼─────────────────────────────────────────────┐
│                        NGINX (Reverse Proxy)                        │
│                    SSL Termination + Rate Limit                      │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────────┐
│                     FASTAPI APPLICATION                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Routers: /auth /videos /clips /jobs /admin /subscriptions  │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  Middleware: Auth Guard │ Rate Limiter │ Subscription Gate   │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  Services: VideoService │ ClipService │ AIJobService         │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                           │
│        ┌────────────────┴────────────────┐                          │
│        │                                 │                          │
│  ┌─────▼──────┐                  ┌───────▼────────┐                │
│  │ PostgreSQL │                  │  Redis (Queue) │                │
│  │  (via ORM) │                  │  Celery Broker │                │
│  └────────────┘                  └───────┬────────┘                │
└──────────────────────────────────────────┼──────────────────────────┘
                                           │
┌──────────────────────────────────────────▼──────────────────────────┐
│                       CELERY WORKERS                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ video_worker │  │  ai_worker   │  │ export_worker│             │
│  │  (yt-dlp)   │  │ (Whisper,    │  │  (FFmpeg,    │             │
│  │  (FFmpeg)   │  │  YOLO, MP)   │  │   Shorts)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                     GPU Server Required ↑                           │
└──────────────────────────────────────────────────────────────────── ┘
                                           │
┌──────────────────────────────────────────▼──────────────────────────┐
│                       SUPABASE PLATFORM                             │
│    Auth (JWT)  │  PostgreSQL Mirror  │  Storage (Videos/Clips)     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Project Folder Structure

### 4.1 Android Project

```
clipforge-android/
├── app/
│   ├── src/main/
│   │   ├── java/com/clipforge/
│   │   │   ├── ClipForgeApp.kt              # Application class
│   │   │   ├── di/                          # Hilt modules
│   │   │   │   ├── NetworkModule.kt
│   │   │   │   ├── DatabaseModule.kt
│   │   │   │   ├── RepositoryModule.kt
│   │   │   │   └── AuthModule.kt
│   │   │   ├── data/
│   │   │   │   ├── remote/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   ├── AuthApi.kt
│   │   │   │   │   │   ├── VideoApi.kt
│   │   │   │   │   │   ├── ClipApi.kt
│   │   │   │   │   │   ├── JobApi.kt
│   │   │   │   │   │   └── SubscriptionApi.kt
│   │   │   │   │   ├── dto/
│   │   │   │   │   │   ├── VideoDto.kt
│   │   │   │   │   │   ├── ClipDto.kt
│   │   │   │   │   │   ├── JobDto.kt
│   │   │   │   │   │   └── SubscriptionDto.kt
│   │   │   │   │   └── interceptor/
│   │   │   │   │       ├── AuthInterceptor.kt
│   │   │   │   │       └── ErrorInterceptor.kt
│   │   │   │   ├── local/
│   │   │   │   │   ├── database/
│   │   │   │   │   │   ├── ClipForgeDatabase.kt
│   │   │   │   │   │   ├── dao/
│   │   │   │   │   │   │   ├── VideoDao.kt
│   │   │   │   │   │   │   └── ClipDao.kt
│   │   │   │   │   │   └── entity/
│   │   │   │   │   │       ├── VideoEntity.kt
│   │   │   │   │   │       └── ClipEntity.kt
│   │   │   │   │   └── datastore/
│   │   │   │   │       ├── UserPreferences.kt
│   │   │   │   │       └── AIPreferences.kt
│   │   │   │   └── repository/
│   │   │   │       ├── AuthRepository.kt
│   │   │   │       ├── VideoRepository.kt
│   │   │   │       ├── ClipRepository.kt
│   │   │   │       └── SubscriptionRepository.kt
│   │   │   ├── domain/
│   │   │   │   ├── model/
│   │   │   │   │   ├── User.kt
│   │   │   │   │   ├── Video.kt
│   │   │   │   │   ├── Clip.kt
│   │   │   │   │   ├── AIJob.kt
│   │   │   │   │   ├── Highlight.kt
│   │   │   │   │   ├── Scene.kt
│   │   │   │   │   ├── ObjectEvent.kt
│   │   │   │   │   ├── GestureEvent.kt
│   │   │   │   │   └── Subscription.kt
│   │   │   │   └── usecase/
│   │   │   │       ├── ImportVideoUseCase.kt
│   │   │   │       ├── CreateManualClipUseCase.kt
│   │   │   │       ├── RunHighlightDetectionUseCase.kt
│   │   │   │       ├── RunSpeechSearchUseCase.kt
│   │   │   │       ├── RunObjectTrackingUseCase.kt
│   │   │   │       ├── RunFaceTrackingUseCase.kt
│   │   │   │       ├── RunGestureTrackingUseCase.kt
│   │   │   │       ├── GenerateShortsUseCase.kt
│   │   │   │       └── GetJobStatusUseCase.kt
│   │   │   ├── presentation/
│   │   │   │   ├── navigation/
│   │   │   │   │   ├── AppNavGraph.kt
│   │   │   │   │   └── Screen.kt
│   │   │   │   ├── screen/
│   │   │   │   │   ├── onboarding/
│   │   │   │   │   │   ├── OnboardingScreen.kt
│   │   │   │   │   │   └── AIModeSelectionScreen.kt
│   │   │   │   │   ├── auth/
│   │   │   │   │   │   ├── LoginScreen.kt
│   │   │   │   │   │   └── AuthViewModel.kt
│   │   │   │   │   ├── home/
│   │   │   │   │   │   ├── HomeScreen.kt
│   │   │   │   │   │   └── HomeViewModel.kt
│   │   │   │   │   ├── import/
│   │   │   │   │   │   ├── ImportVideoScreen.kt
│   │   │   │   │   │   └── ImportVideoViewModel.kt
│   │   │   │   │   ├── clips/
│   │   │   │   │   │   ├── AIClipsScreen.kt
│   │   │   │   │   │   ├── ClipDetailScreen.kt
│   │   │   │   │   │   ├── ManualClipScreen.kt
│   │   │   │   │   │   └── ClipsViewModel.kt
│   │   │   │   │   ├── projects/
│   │   │   │   │   │   ├── ProjectsScreen.kt
│   │   │   │   │   │   └── ProjectsViewModel.kt
│   │   │   │   │   ├── subscription/
│   │   │   │   │   │   ├── SubscriptionScreen.kt
│   │   │   │   │   │   └── SubscriptionViewModel.kt
│   │   │   │   │   └── settings/
│   │   │   │   │       ├── SettingsScreen.kt
│   │   │   │   │       └── SettingsViewModel.kt
│   │   │   │   └── component/
│   │   │   │       ├── VideoThumbnailCard.kt
│   │   │   │       ├── ClipCard.kt
│   │   │   │       ├── JobProgressBar.kt
│   │   │   │       ├── HighlightTimeline.kt
│   │   │   │       ├── GestureEventItem.kt
│   │   │   │       ├── ScenePreviewGrid.kt
│   │   │   │       └── PremiumGateDialog.kt
│   │   │   ├── local_ai/
│   │   │   │   ├── LocalAIManager.kt
│   │   │   │   ├── WhisperLocal.kt
│   │   │   │   ├── YoloLocal.kt
│   │   │   │   └── SceneDetectorLocal.kt
│   │   │   └── util/
│   │   │       ├── TimeFormatter.kt
│   │   │       ├── VideoExtensions.kt
│   │   │       └── SubscriptionChecker.kt
│   │   └── res/
│   │       ├── values/
│   │       │   ├── strings.xml
│   │       │   └── themes.xml
│   │       └── raw/
│   │           └── (TFLite / ONNX model files untuk Local AI)
│   └── build.gradle.kts
├── gradle/
└── settings.gradle.kts
```

### 4.2 Backend Project

```
clipforge-backend/
├── app/
│   ├── main.py                         # FastAPI app entry point
│   ├── config.py                       # Settings dari env vars
│   ├── dependencies.py                 # Auth, DB, Redis dependencies
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py               # Main v1 router aggregator
│   │   │   ├── auth.py                 # /auth endpoints
│   │   │   ├── videos.py               # /videos endpoints
│   │   │   ├── clips.py                # /clips endpoints
│   │   │   ├── jobs.py                 # /jobs endpoints (polling)
│   │   │   ├── subscriptions.py        # /subscriptions endpoints
│   │   │   └── admin.py                # /admin endpoints
│   ├── core/
│   │   ├── auth.py                     # JWT decode, Supabase verification
│   │   ├── rate_limiter.py             # Redis-backed rate limiting
│   │   ├── subscription_gate.py        # Plan enforcement middleware
│   │   └── exceptions.py              # Custom HTTP exceptions
│   ├── models/
│   │   ├── base.py                     # Base SQLAlchemy model
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── clip.py
│   │   ├── ai_job.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   └── usage_log.py
│   ├── schemas/
│   │   ├── video.py                    # Pydantic request/response schemas
│   │   ├── clip.py
│   │   ├── job.py
│   │   └── subscription.py
│   ├── services/
│   │   ├── video_service.py            # Business logic: import, metadata
│   │   ├── clip_service.py             # Business logic: manual clip
│   │   ├── ai_job_service.py           # Create/track AI jobs
│   │   ├── subscription_service.py     # Plan checks, quota enforcement
│   │   └── storage_service.py          # Supabase Storage upload/download
│   ├── tasks/                          # Celery task definitions
│   │   ├── celery_app.py               # Celery factory
│   │   ├── video_tasks.py              # yt-dlp download task
│   │   ├── ai_tasks/
│   │   │   ├── highlight_task.py       # AI Highlight Detection
│   │   │   ├── whisper_task.py         # Whisper transcription
│   │   │   ├── scene_task.py           # Scene detection (PySceneDetect)
│   │   │   ├── yolo_task.py            # YOLOv8 object tracking
│   │   │   ├── face_task.py            # MediaPipe face tracking
│   │   │   ├── gesture_task.py         # MediaPipe + YOLO Pose gesture
│   │   │   └── shorts_task.py          # Shorts generation pipeline
│   │   └── export_tasks.py             # FFmpeg clip export + watermark
│   └── db/
│       ├── session.py                  # Async DB session factory
│       └── migrations/                 # Alembic migration files
│           └── versions/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx/
│   └── nginx.conf
├── requirements.txt
└── .env.example
```

### 4.3 Admin Panel (Web)

```
clipforge-admin/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Users.tsx
│   │   ├── Subscriptions.tsx
│   │   ├── JobQueue.tsx
│   │   ├── AIUsage.tsx
│   │   └── Settings.tsx
│   ├── components/
│   ├── api/
│   └── hooks/
├── package.json
└── vite.config.ts
```

---

## 5. Database Schema

### 5.1 Entity Relationship Diagram (Simplified)

```
users ──< subscriptions
users ──< videos ──< clips
users ──< ai_jobs ──< job_results
videos ──< ai_jobs
ai_jobs ──< job_results
users ──< usage_logs
users ──< payments
```

### 5.2 Table Definitions

#### `users`
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_uid    TEXT UNIQUE NOT NULL,         -- Supabase Auth user ID
    email           TEXT UNIQUE NOT NULL,
    full_name       TEXT,
    avatar_url      TEXT,
    plan            TEXT NOT NULL DEFAULT 'free', -- 'free' | 'premium'
    ai_mode         TEXT NOT NULL DEFAULT 'server',-- 'local' | 'server'
    is_admin        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `subscriptions`
```sql
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan            TEXT NOT NULL,                -- 'free' | 'premium'
    status          TEXT NOT NULL,                -- 'active' | 'expired' | 'cancelled'
    started_at      TIMESTAMPTZ NOT NULL,
    expires_at      TIMESTAMPTZ,
    payment_provider TEXT,                        -- 'google_play' | 'stripe' | 'manual'
    provider_sub_id TEXT,                         -- External subscription ID
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `videos`
```sql
CREATE TABLE videos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    youtube_url     TEXT NOT NULL,
    youtube_id      TEXT NOT NULL,
    title           TEXT,
    thumbnail_url   TEXT,
    duration_seconds INTEGER,
    resolution      TEXT,                         -- '720p' | '1080p' | '4k'
    file_path       TEXT,                         -- Supabase Storage path
    status          TEXT NOT NULL DEFAULT 'pending', -- 'pending' | 'downloading' | 'ready' | 'error'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `clips`
```sql
CREATE TABLE clips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    ai_job_id       UUID REFERENCES ai_jobs(id),
    title           TEXT,
    start_time      FLOAT NOT NULL,               -- seconds
    end_time        FLOAT NOT NULL,               -- seconds
    duration        FLOAT,
    output_path     TEXT,                         -- Supabase Storage path
    thumbnail_path  TEXT,
    resolution      TEXT,
    has_watermark   BOOLEAN NOT NULL DEFAULT TRUE,
    clip_type       TEXT NOT NULL,                -- 'manual' | 'highlight' | 'speech' | 'scene' | 'object' | 'face' | 'gesture' | 'short'
    highlight_score FLOAT,                        -- 0.0 - 1.0
    metadata        JSONB,                        -- arbitrary AI metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `ai_jobs`
```sql
CREATE TABLE ai_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id        UUID NOT NULL REFERENCES videos(id),
    celery_task_id  TEXT,                         -- Celery task ID for polling
    job_type        TEXT NOT NULL,                -- 'highlight' | 'speech_search' | 'scene' | 'object' | 'face' | 'gesture' | 'shorts'
    status          TEXT NOT NULL DEFAULT 'queued',-- 'queued' | 'processing' | 'done' | 'failed'
    priority        INTEGER NOT NULL DEFAULT 5,   -- 1=highest (premium), 10=lowest (free)
    params          JSONB,                        -- e.g. {"query": "giveaway"} for speech_search
    progress        INTEGER DEFAULT 0,            -- 0-100
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    finished_at     TIMESTAMPTZ
);
```

#### `job_results`
```sql
CREATE TABLE job_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_job_id       UUID NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,
    result_type     TEXT NOT NULL,                -- 'highlight' | 'timestamp' | 'scene' | 'gesture' | etc.
    start_time      FLOAT,
    end_time        FLOAT,
    label           TEXT,                         -- e.g. "Hand raised", "Person detected"
    score           FLOAT,                        -- confidence or highlight score
    metadata        JSONB,                        -- bounding box, landmark coords, etc.
    clip_id         UUID REFERENCES clips(id)     -- generated clip (if auto-clipped)
);
```

#### `payments`
```sql
CREATE TABLE payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    amount          NUMERIC(10, 2),
    currency        TEXT DEFAULT 'USD',
    provider        TEXT,                         -- 'google_play' | 'stripe'
    provider_tx_id  TEXT,
    status          TEXT,                         -- 'pending' | 'success' | 'failed' | 'refunded'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `usage_logs`
```sql
CREATE TABLE usage_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    action          TEXT NOT NULL,                -- 'video_import' | 'clip_export' | 'ai_job'
    video_id        UUID REFERENCES videos(id),
    ai_job_id       UUID REFERENCES ai_jobs(id),
    date            DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for daily quota checks
CREATE INDEX idx_usage_logs_user_date ON usage_logs(user_id, date);
```

### 5.3 Daily Quota Enforcement Query

```sql
-- Check berapa video yang diimport user hari ini
SELECT COUNT(*) FROM usage_logs
WHERE user_id = $1
  AND action = 'video_import'
  AND date = CURRENT_DATE;
```

---

## 6. API Specification

**Base URL:** `https://api.clipforge.app/v1`
**Auth:** Bearer JWT (Supabase Access Token)

### 6.1 Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register dengan email & password |
| `POST` | `/auth/login` | Login dengan email & password |
| `POST` | `/auth/google` | Login dengan Google OAuth token |
| `POST` | `/auth/refresh` | Refresh access token |
| `DELETE` | `/auth/logout` | Logout & revoke token |
| `GET` | `/auth/me` | Profil user yang sedang login |

### 6.2 Videos

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/videos/import` | Import video dari YouTube URL |
| `GET` | `/videos` | List semua video milik user |
| `GET` | `/videos/{id}` | Detail satu video |
| `DELETE` | `/videos/{id}` | Hapus video |
| `GET` | `/videos/{id}/metadata` | Metadata YouTube (judul, thumbnail, durasi) |

**Request: `POST /videos/import`**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=XXXXXXX"
}
```

**Response:**
```json
{
  "id": "uuid",
  "youtube_id": "XXXXXXX",
  "title": "Video Title",
  "thumbnail_url": "https://i.ytimg.com/...",
  "duration_seconds": 3600,
  "status": "downloading"
}
```

### 6.3 Clips

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/clips/manual` | Buat clip manual (start/end time) |
| `GET` | `/clips` | List clip milik user |
| `GET` | `/clips/{id}` | Detail satu clip |
| `DELETE` | `/clips/{id}` | Hapus clip |
| `GET` | `/clips/{id}/download` | Download URL clip |

**Request: `POST /clips/manual`**
```json
{
  "video_id": "uuid",
  "start_time": 30.5,
  "end_time": 90.0,
  "title": "My Clip"
}
```

### 6.4 AI Jobs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/jobs/highlight` | Run AI Highlight Detection |
| `POST` | `/jobs/speech-search` | Run Speech Search |
| `POST` | `/jobs/scene-detection` | Run Scene Detection |
| `POST` | `/jobs/object-tracking` | Run Object Tracking (Premium) |
| `POST` | `/jobs/face-tracking` | Run Face Tracking (Premium) |
| `POST` | `/jobs/gesture-tracking` | Run Gesture Tracking (Premium) |
| `POST` | `/jobs/shorts` | Generate Shorts (Premium) |
| `GET` | `/jobs/{id}` | Status & progress job |
| `GET` | `/jobs/{id}/results` | Hasil lengkap job |
| `GET` | `/jobs` | List jobs milik user |

**Request: `POST /jobs/speech-search`**
```json
{
  "video_id": "uuid",
  "query": "giveaway",
  "auto_clip": true,
  "clip_padding_seconds": 5
}
```

**Request: `POST /jobs/gesture-tracking`**
```json
{
  "video_id": "uuid",
  "gestures": ["pointing", "hand_raised", "thumbs_up", "wave", "clap", "facing_camera"],
  "auto_clip": true
}
```

**Response: `GET /jobs/{id}/results`**
```json
{
  "job_id": "uuid",
  "job_type": "gesture_tracking",
  "status": "done",
  "results": [
    {
      "timestamp": 135.0,
      "label": "Person pointing right",
      "score": 0.94,
      "clip_id": "uuid"
    },
    {
      "timestamp": 248.5,
      "label": "Hand raised",
      "score": 0.88,
      "clip_id": "uuid"
    }
  ]
}
```

### 6.5 Subscriptions

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/subscriptions/me` | Status langganan user saat ini |
| `POST` | `/subscriptions/upgrade` | Upgrade ke Premium |
| `POST` | `/subscriptions/cancel` | Cancel langganan |
| `POST` | `/subscriptions/verify` | Verifikasi purchase dari Google Play |

### 6.6 Admin

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/users` | List semua user (dengan filter & pagination) |
| `PUT` | `/admin/users/{id}/plan` | Override plan user |
| `GET` | `/admin/subscriptions` | Semua subscription aktif |
| `GET` | `/admin/jobs` | Job queue overview |
| `GET` | `/admin/stats` | Statistik penggunaan agregat |
| `GET` | `/admin/ai-usage` | Log penggunaan AI per model |

---

## 7. AI Pipeline Architecture

### 7.1 Server AI Pipeline

```
YouTube URL
    │
    ▼
[1] yt-dlp Worker
    ├── Download video (best quality sesuai plan)
    ├── Extract metadata (title, thumbnail, duration)
    └── Upload ke Supabase Storage
         │
         ▼
[2] Analysis Workers (paralel atau sequential sesuai job_type)
    │
    ├── Highlight Detection
    │   ├── FFmpeg: extract audio → spectrogram
    │   ├── Audio energy analysis → high-energy timestamps
    │   ├── Whisper: transcript → keyword/emotion scoring
    │   └── PySceneDetect: scene change frequency
    │
    ├── Speech Search
    │   ├── Whisper: full transcription
    │   ├── Word-level timestamp lookup
    │   └── Clip generation (FFmpeg) dengan padding
    │
    ├── Scene Detection
    │   ├── PySceneDetect: threshold-based scene cut detection
    │   └── FFmpeg: generate thumbnail per scene
    │
    ├── Object Tracking (YOLOv8)
    │   ├── Frame-by-frame inference (sampled setiap N frame)
    │   ├── Filter by target class (person, car, cat, dog, dll.)
    │   └── Merge adjacent detection → timestamp range
    │
    ├── Face Tracking (MediaPipe Face Detection)
    │   ├── Face landmark detection per frame
    │   ├── Track face ID across frames
    │   └── Generate clip saat wajah aktif
    │
    ├── Gesture Tracking (MediaPipe + YOLO Pose)
    │   ├── Pose estimation: keypoint coordinates
    │   ├── Rule-based gesture classifier:
    │   │   ├── pointing: wrist angle + elbow extension
    │   │   ├── hand_raised: wrist Y < shoulder Y
    │   │   ├── wave: wrist X oscillation
    │   │   ├── thumbs_up: thumb keypoint direction
    │   │   ├── clap: wrist proximity bilateral
    │   │   └── facing_camera: nose visibility score
    │   └── Generate timestamp events + auto clip
    │
    └── Shorts Generator
        ├── Input: selected clip atau highlight
        ├── FFmpeg: crop ke 9:16 aspect ratio
        ├── Subject detection (YOLO) → center crop
        ├── Whisper: subtitle generation (SRT)
        ├── FFmpeg: burn subtitles ke video
        └── Output: TikTok/Reels/Shorts-ready MP4
             │
             ▼
[3] Export Worker
    ├── Apply watermark jika Free plan (FFmpeg overlay)
    ├── Encode output sesuai plan (720p max Free, 4K Premium)
    ├── Upload ke Supabase Storage
    └── Update DB: clip.output_path, ai_job.status = 'done'
```

### 7.2 Local AI Pipeline (On-Device Android)

```
Mode Local AI (tanpa upload video ke server):
    │
    ▼
Android WorkManager Task
    ├── yt-dlp via shell process (Termux-compatible) → lokal storage
    ├── Whisper TFLite (quantized tiny/base model) → transcript
    ├── YOLOv8 ONNX (nano model) → object detection frames
    └── FFmpeg Android (via FFmpegKit) → cut & export clips
```

**Catatan:** Local AI menggunakan model yang lebih ringan (quantized). Akurasi lebih rendah dibanding Server AI.

### 7.3 Highlight Score Algorithm

```
highlight_score = (
  0.35 * audio_energy_score +     -- peak audio/volume burst
  0.25 * transcript_score +        -- kata emosional/keyword density
  0.20 * scene_change_rate +       -- perubahan visual cepat
  0.20 * visual_activity_score     -- motion vector magnitude
)
```

---

## 8. Android Architecture

### 8.1 Architecture Pattern: MVVM + Clean Architecture

```
┌──────────────────────────────────────────────┐
│              Presentation Layer              │
│  Composable Screens  ←→  ViewModels (Hilt)   │
│         ↑ UI State / Events ↑                │
└──────────────────────────┬───────────────────┘
                           │ UseCases
┌──────────────────────────▼───────────────────┐
│               Domain Layer                   │
│  Use Cases  ←  Domain Models  → Interfaces   │
└──────────────────────────┬───────────────────┘
                           │ Repository interfaces
┌──────────────────────────▼───────────────────┐
│                Data Layer                    │
│  Repositories → Remote DataSource (Retrofit) │
│              → Local DataSource (Room)       │
│              → Preferences (DataStore)       │
└──────────────────────────────────────────────┘
```

### 8.2 State Management

Semua ViewModel menggunakan **Kotlin StateFlow + sealed class** untuk UI state:

```kotlin
// Contoh pola state untuk AI Job
sealed class JobUiState {
    object Idle : JobUiState()
    object Loading : JobUiState()
    data class Queued(val jobId: String) : JobUiState()
    data class Processing(val progress: Int) : JobUiState()
    data class Success(val results: List<JobResult>) : JobUiState()
    data class Error(val message: String) : JobUiState()
}
```

### 8.3 Navigation Graph

```
AppNavGraph
├── OnboardingScreen (first launch only)
│   └── AIModeSelectionScreen
├── AuthGraph
│   ├── LoginScreen
│   └── (Register via Supabase)
└── MainGraph (BottomNav)
    ├── HomeScreen
    ├── ImportVideoScreen
    │   ├── VideoMetadataPreview
    │   └── ClipOptionsScreen
    │       ├── ManualClipScreen
    │       ├── AIHighlightScreen
    │       ├── SpeechSearchScreen
    │       ├── SceneDetectionScreen
    │       ├── ObjectTrackingScreen  [Premium]
    │       ├── FaceTrackingScreen    [Premium]
    │       ├── GestureTrackingScreen [Premium]
    │       └── ShortsGeneratorScreen [Premium]
    ├── AIClipsScreen
    │   └── ClipDetailScreen
    ├── ProjectsScreen
    ├── SubscriptionScreen
    └── SettingsScreen
```

### 8.4 Job Polling Strategy

Karena AI job bisa memakan waktu lama (1–10 menit), Android menggunakan **polling dengan exponential backoff**:

```
Poll interval schedule:
0s → 3s → 5s → 10s → 15s → 30s → 60s (cap)

Android WorkManager + Coroutines:
- Foreground service selama job aktif
- Push notification saat job selesai
- Result disimpan di Room DB untuk offline access
```

---

## 9. UI/UX Flow

### 9.1 First Launch Flow

```
App Launch
    │
    ▼
[Onboarding] Pilih AI Mode
    ├── Local AI  → simpan ke DataStore
    └── Server AI → simpan ke DataStore
         │
         ▼
[Auth] Login Screen
    ├── Google Sign-In
    └── Email & Password
         │
         ▼
[Home] Dashboard
```

### 9.2 Import & Clip Flow

```
[Home] Tap "Import Video"
    │
    ▼
Paste YouTube URL
    │
    ▼
Backend: yt-dlp fetch metadata
    │
    ▼
Preview Card:
┌──────────────────────────┐
│  [Thumbnail]             │
│  Judul Video             │
│  Durasi: 1:23:45         │
│  [Pilih Aksi AI]         │
└──────────────────────────┘
    │
    ├── Manual Clip
    │   └── Time Picker (Start / End) → Submit → Clip ready
    │
    ├── AI Highlight → Submit Job → Progress Bar → Results
    │
    ├── Speech Search → Input kata → Submit → Timestamps + Clips
    │
    ├── Scene Detection → Submit → Scene Grid → Export pilihan
    │
    ├── Object Tracking [🔒 Premium]
    │
    ├── Face Tracking [🔒 Premium]
    │
    ├── Gesture Tracking [🔒 Premium]
    │   └── Checklist gesture → Submit → Timeline events → Auto clip
    │
    └── Shorts Generator [🔒 Premium]
        └── Select clip → Generate → Download MP4
```

### 9.3 Premium Gate Dialog

Saat Free user mengakses fitur Premium:

```
┌─────────────────────────────────┐
│  ⭐ Fitur Premium                │
│                                 │
│  [Nama Fitur] tersedia di       │
│  ClipForge Premium.             │
│                                 │
│  ✓ Unlimited video              │
│  ✓ Face & Gesture Tracking      │
│  ✓ Export 4K                    │
│  ✓ No Watermark                 │
│                                 │
│  [Upgrade Sekarang]  [Nanti]    │
└─────────────────────────────────┘
```

### 9.4 Gesture Tracking Result Screen

```
Gesture Timeline:
┌────────────────────────────────────────┐
│  00:02:15 → Person pointing right  [►] │
│  00:04:08 → Hand raised            [►] │
│  00:08:22 → Thumbs up              [►] │
│  00:11:45 → Wave                   [►] │
└────────────────────────────────────────┘
[Export Semua] [Export Pilihan]
```

---

## 10. Subscription & Entitlement System

### 10.1 Plan Comparison

| Feature | Free | Premium |
|---|---|---|
| Video per hari | 3 | Unlimited |
| Durasi video max | 1 menit | Unlimited |
| Kualitas output max | 720p | 4K |
| Manual Clip | ✅ | ✅ |
| Basic Highlight | ✅ | ✅ |
| Scene Detection | ✅ | ✅ |
| Object Tracking | ❌ | ✅ |
| Face Tracking | ❌ | ✅ |
| Gesture Tracking | ❌ | ✅ |
| Speech Search | ❌ | ✅ |
| Shorts Generator | ❌ | ✅ |
| Batch Processing | ❌ | ✅ |
| Watermark | ✅ Ada | ❌ Tidak |
| Queue Priority | Rendah (5) | Tinggi (1) |

### 10.2 Enforcement Flow (Backend Middleware)

```python
# subscription_gate.py (pseudo)
class SubscriptionGate:
    async def check(user, required_plan, action):
        if required_plan == "premium" and user.plan == "free":
            raise PremiumRequiredException()

        if user.plan == "free":
            daily_count = await get_daily_usage(user.id, "video_import")
            if daily_count >= 3:
                raise DailyLimitExceededException()
```

### 10.3 Payment Flow (Google Play)

```
Android → Google Play Billing
    │
    ├── Purchase confirmed di client
    │
    ▼
POST /subscriptions/verify
    Body: { purchase_token, product_id }
    │
    ▼
Backend → Google Play Developer API verify
    │
    ▼
Update DB: user.plan = 'premium'
          subscription.status = 'active'
    │
    ▼
Return 200 OK → Android updates UI state
```

---

## 11. Queue & Job System

### 11.1 Celery Queue Configuration

```python
# Dua queue berdasarkan prioritas

CELERY_TASK_ROUTES = {
    'tasks.ai_tasks.*': {'queue': 'ai_jobs'},
    'tasks.video_tasks.*': {'queue': 'video_download'},
    'tasks.export_tasks.*': {'queue': 'export'},
}

# Premium users → priority 1
# Free users    → priority 5
```

### 11.2 Job Lifecycle

```
Client Submit Job
       │
       ▼
POST /jobs/{type}
       │
       ▼
[DB] ai_jobs.status = 'queued'
[Redis] Task dikirim ke Celery
       │
       ▼
Celery Worker pick-up (sesuai priority)
       │
       ▼
[DB] ai_jobs.status = 'processing'
     ai_jobs.started_at = NOW()
     ai_jobs.progress = 0..100 (update berkala)
       │
       ▼
Worker selesai
       │
    ┌──┴──┐
  Done   Error
    │      │
    ▼      ▼
status=  status=
'done'  'failed'
job_results  error_message
inserted     saved
       │
       ▼
Client polling GET /jobs/{id}
       │
       ▼
Tampilkan hasil di Android
```

---

## 12. Admin Panel Architecture

### 12.1 Stack

- **Framework:** React + TypeScript + Vite
- **UI Library:** shadcn/ui + Tailwind CSS
- **Auth:** Supabase Auth (admin role check dari `users.is_admin`)
- **Data Fetching:** React Query → FastAPI Admin endpoints

### 12.2 Halaman Admin

**Dashboard**
- Total users, active subscriptions, revenue (MTD)
- AI job count per hari (chart)
- Error rate per job type

**Users Page**
- Tabel: user, email, plan, join date, last active
- Filter by plan, search by email
- Action: Override plan, suspend user

**Job Queue Page**
- Live view of queued, processing, done, failed jobs
- Filter by type, status, user
- Action: Re-queue failed job, cancel job

**AI Usage Page**
- GPU time per model (Whisper, YOLO, MediaPipe)
- Cost estimation per model per bulan
- Top consumers by user

**Subscription Page**
- Active subscriptions list
- Revenue metrics
- Churn rate

---

## 13. Infrastructure & Deployment

### 13.1 Docker Services

```yaml
# docker-compose.yml (ringkasan)

services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    depends_on: [api]

  api:
    build: ./clipforge-backend
    environment: [DATABASE_URL, REDIS_URL, ...]
    depends_on: [db, redis]

  worker_video:
    build: ./clipforge-backend
    command: celery -A app.tasks.celery_app worker -Q video_download -c 4
    depends_on: [redis, db]

  worker_ai:
    build: ./clipforge-backend
    command: celery -A app.tasks.celery_app worker -Q ai_jobs -c 2
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]   # GPU required
    depends_on: [redis, db]

  worker_export:
    build: ./clipforge-backend
    command: celery -A app.tasks.celery_app worker -Q export -c 4
    depends_on: [redis, db]

  db:
    image: postgres:16
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine

  flower:
    image: mher/flower
    command: celery flower --broker=redis://redis:6379/0
    ports: ["5555:5555"]
    depends_on: [redis]
```

### 13.2 Nginx Configuration

```nginx
# /nginx/nginx.conf

upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name api.clipforge.app;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.clipforge.app;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req zone=api_limit burst=20 nodelay;

    location /v1/ {
        proxy_pass http://api;
        proxy_set_header Authorization $http_authorization;
        client_max_body_size 0;
    }
}
```

### 13.3 CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build & push Docker image
        run: docker build -t clipforge-api .
      - name: Deploy ke server
        run: ssh deploy@server "cd /app && docker-compose pull && docker-compose up -d"

  deploy-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build APK/AAB
        run: ./gradlew bundleRelease
      - name: Upload ke Play Store
        uses: r0adkll/upload-google-play@v1
```

---

## 14. Environment Variables

### 14.1 Backend `.env`

```env
# ── Database ──────────────────────────────────
DATABASE_URL=postgresql+asyncpg://clipforge:password@db:5432/clipforge

# ── Redis ─────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── Supabase ──────────────────────────────────
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_STORAGE_BUCKET=clipforge-videos

# ── Google Play Billing ───────────────────────
GOOGLE_PLAY_PACKAGE_NAME=com.clipforge.app
GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=/secrets/google-play.json

# ── AI Models ─────────────────────────────────
WHISPER_MODEL_SIZE=base                # tiny | base | small | medium
YOLO_MODEL_PATH=/models/yolov8n.pt
YOLO_POSE_MODEL_PATH=/models/yolov8n-pose.pt

# ── FFmpeg ────────────────────────────────────
FFMPEG_PATH=/usr/bin/ffmpeg
WATERMARK_PATH=/assets/watermark.png

# ── App ───────────────────────────────────────
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production                 # development | production
LOG_LEVEL=INFO
MAX_FREE_VIDEOS_PER_DAY=3
MAX_FREE_VIDEO_DURATION_SECONDS=60
```

### 14.2 Android `local.properties`

```properties
# Tidak di-commit ke Git
CLIPFORGE_API_BASE_URL=https://api.clipforge.app/v1/
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
```

---

## 15. Security Architecture

### 15.1 Authentication Flow

```
Android App
    │ Google Sign-In Token / Email+Pass
    ▼
Supabase Auth → returns JWT (access_token)
    │
    ▼
Android menyimpan JWT di DataStore (encrypted)
    │
Android → setiap request:
    Header: Authorization: Bearer <access_token>
    │
    ▼
FastAPI middleware:
    ├── Decode JWT menggunakan SUPABASE_JWT_SECRET
    ├── Extract supabase_uid
    ├── Lookup user di DB
    └── Inject user object ke request context
```

### 15.2 Security Checklist

| Layer | Kontrol |
|---|---|
| **Transport** | HTTPS-only, TLS 1.3 |
| **Auth** | JWT dengan expiry + refresh token rotation |
| **API** | Rate limiting per IP + per user (Redis) |
| **Subscription** | Server-side enforcement (tidak bisa di-bypass dari client) |
| **Storage** | Supabase Storage dengan presigned URL (akses terbatas) |
| **Input Validation** | Pydantic v2 di semua endpoint |
| **SQL** | ORM queries only, no raw SQL concat |
| **Admin** | `is_admin` flag diverifikasi di setiap request |
| **Secrets** | Semua secret di environment variable, tidak hardcoded |

---

## 16. Roadmap: MVP to Production

### Phase 1 — MVP (Minggu 1–6)

**Goal:** Produk dapat digunakan end-to-end, fitur inti berjalan.

| Deliverable | Detail |
|---|---|
| ✅ Android App Skeleton | Navigation, Hilt DI, Retrofit setup |
| ✅ Supabase Auth | Google + Email login berfungsi |
| ✅ Import Video | Paste URL → metadata + thumbnail tampil |
| ✅ Manual Clip | Start/End time → FFmpeg cut → download |
| ✅ Basic Highlight | Audio-based highlight detection |
| ✅ Scene Detection | PySceneDetect integration |
| ✅ Free Plan Limits | Quota enforcement, watermark |
| ✅ Backend API | FastAPI + PostgreSQL + Redis + Celery |
| ✅ Docker Compose | Local dev environment lengkap |

### Phase 2 — Feature Complete (Minggu 7–12)

**Goal:** Semua fitur AI aktif, Premium plan live.

| Deliverable | Detail |
|---|---|
| 🔶 Speech Search | Whisper integration + word timestamp |
| 🔶 Object Tracking | YOLOv8 pipeline |
| 🔶 Face Tracking | MediaPipe face detection |
| 🔶 Gesture Tracking | MediaPipe + YOLO Pose + rule classifier |
| 🔶 Shorts Generator | 9:16 crop + subtitle burn |
| 🔶 Premium Plan | Google Play Billing integration |
| 🔶 Admin Panel | User, job, subscription management |
| 🔶 Push Notification | Job complete notification |

### Phase 3 — Production Hardening (Minggu 13–18)

**Goal:** Stabilitas, performa, dan siap skala.

| Deliverable | Detail |
|---|---|
| 🔷 Local AI Mode | TFLite/ONNX Whisper & YOLO on-device |
| 🔷 GPU Auto-Scaling | Worker scale out/in berdasarkan queue depth |
| 🔷 Caching Layer | Redis cache untuk job results & metadata |
| 🔷 Batch Processing | Proses banyak video sekaligus (Premium) |
| 🔷 Analytics | Usage dashboard, funnel analysis |
| 🔷 Error Monitoring | Sentry integration |
| 🔷 Load Testing | k6 / Locust stress test |
| 🔷 Play Store Launch | Produksi AAB, listing, screenshots |

### Phase 4 — Growth (Bulan 5+)

| Deliverable | Detail |
|---|---|
| ⬜ Multi-language | Whisper multilingual support |
| ⬜ Team/Agency Plan | Multi-user workspace |
| ⬜ API Public | Developer API access (paid tier) |
| ⬜ Web Client | Browser-based versi untuk desktop user |
| ⬜ Custom AI Model | Fine-tuned highlight model per niche |

---

*Dokumen ini adalah living document. Update setiap sprint review.*
*ClipForge Architecture v1.0.0 — Confidential*
