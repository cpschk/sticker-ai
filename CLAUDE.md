# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fullstack monorepo for AI-powered sticker generation with emotion detection. Consists of:
- **`backend/`** — Python FastAPI service: text analysis, emotion detection, avatar pose selection, image generation
- **`mobile/`** — React Native Expo app (iOS, Android, Web)
- **`mobile-kotlin/`** — Native Android app (Kotlin, MVVM) — has its own `CLAUDE.md`
- **`android-keyboard/`** — Android custom IME keyboard that surfaces sticker suggestions while typing

## Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run dev server (http://localhost:8000)
uvicorn main:app --reload

# Run with explicit host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Quick integration test (no pytest needed)
python quick_test.py

# Run tests
pytest
pytest test_emotions.py          # single file
pytest --cov                     # with coverage

# Lint & format
black .
flake8 .
mypy app/
```

API docs available at `http://localhost:8000/docs` when running.

### Mobile (React Native)

```bash
cd mobile

npm install
npm start          # Expo dev server
npm run android
npm run ios
npm run web
```

### Mobile Kotlin / Android Keyboard

Both Android projects use the Gradle wrapper. From either `mobile-kotlin/` or `android-keyboard/`:

```bash
./gradlew assembleDebug        # build debug APK
./gradlew installDebug         # install on connected device/emulator
./gradlew test                 # unit tests
./gradlew connectedAndroidTest # instrumented tests (requires device/emulator)
./gradlew lint
```

## Architecture

### Backend (`backend/`)

Follows a **Routes → Services → Models** pattern. No database — all data is in-memory mock structures.

```
backend/
├── main.py                          # FastAPI app, CORS, router registration
├── app/
│   ├── models/
│   │   ├── __init__.py              # All Pydantic request/response schemas
│   │   └── avatar_pose.py           # AvatarPose dataclass + AVATAR_POSES mock data
│   ├── routes/
│   │   ├── health.py                # GET /health
│   │   ├── analyze.py               # POST /api/v1/analyze-text
│   │   ├── emotions.py              # POST /api/v1/detect-emotion
│   │   └── stickers.py              # POST /api/v1/suggest-sticker
│   └── services/
│       ├── text_analyzer.py
│       ├── emotion_detector.py
│       ├── sticker_generator.py
│       ├── avatar_service.py
│       └── image_manipulation.py
├── quick_test.py                    # Validates all 5 services (no server needed)
├── test_emotions.py                 # 21 emotion detection test cases
├── test_integrated_analysis.py      # Text analysis + emotion integration (6 cases)
├── test_suggest_sticker_integration.py  # Full endpoint simulation (8 cases)
├── test_suggest_sticker_with_image.py   # Image generation test, writes PNG to disk
├── demo_*.py / example_*.py         # Standalone demo scripts
└── *.md / *.txt                     # Additional per-feature documentation
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/detect-emotion` | Emotion detection only |
| POST | `/api/v1/analyze-text` | Text analysis + emotion detection combined |
| POST | `/api/v1/suggest-sticker` | text → emotion + avatar pose + sticker list (no image) |
| POST | `/api/v1/generate-image` | On-demand sticker image generation (avatar + speech bubble) |

### Request Flow

**`POST /api/v1/suggest-sticker`** (fast, called on every keystroke debounce):
1. `TextAnalyzerService.analyze()` → keywords, sentiment, theme
2. `EmotionDetectorService.detect()` → emotion, intensity (0.0–1.0), intensity_level, confidence
3. `AvatarPoseSelectionService.select_best_pose()` → best `AvatarPose` matching emotion + intensity
4. `StickerGeneratorService.generate_suggestions()` → 5 sticker dicts from `STICKER_LIBRARY`
5. Returns `StickerSuggestionResponse` — `generated_image_base64` is always `null`

**`POST /api/v1/generate-image`** (called only when user taps a sticker bubble):
- Accepts `{text, emotion}`; loads `sticker_image_test.png` as base avatar
- Calls `generate_sticker()` → PIL image with speech bubble → base64 PNG in `{image_base64}`

### Services

**`emotion_detector.py`** — `EmotionDetectorService`
- Detects 6 Spanish emotions: `risa`, `sorpresa`, `enojo`, `tristeza`, `confusión`, `sarcasmo`
- Uses hardcoded keyword lists + regex patterns (no ML)
- Intensity calculation factors in character repetitions (e.g., "jajaja"), uppercase ratio, and punctuation emphasis
- Returns all 6 emotion scores ranked; intensity_level: `"baja"` (<0.4), `"media"` (<0.7), `"alta"` (≥0.7)

**`text_analyzer.py`** — `TextAnalyzerService`
- `extract_keywords()` — regex-based, removes stopwords
- `analyze_sentiment()` — keyword-based → `"positive"`, `"negative"`, `"neutral"`
- `detect_theme()` — keyword matching → `celebration`, `love`, `humor`, `nature`, `work`, `general`

**`avatar_service.py`** — `AvatarPoseSelectionService`
- `select_best_pose(emotion, prefer_intensity)` — closest intensity match
- `select_best_pose_weighted(emotion)` — weighted probability favoring 0.4–0.7 range
- `select_pose_by_intensity_range(emotion, min, max)` — random pose within range
- `select_pose_sequence(emotion, count)` — returns list for animation sequences

**`sticker_generator.py`** — `StickerGeneratorService`
- `STICKER_LIBRARY`: 18 stickers across 6 themes (3 per theme)
- Returns sticker suggestions with UUID id, name, description, style, tags

**`image_manipulation.py`** — `ImageWithSpeechBubble`
- `add_speech_bubble_from_image(image, text, style, ...)` — adds comic speech bubble to PIL Image
- Bubble color maps to emotion (risa→yellow, sorpresa→magenta, enojo→red, tristeza→blue, confusión→purple, sarcasmo→gray)
- Supports `"comic"` style (jagged edges) and normal style
- Font size adapts to text length; text auto-wraps

### Data Models (`app/models/`)

**`avatar_pose.py`**
- `PoseEmotion` enum: `RISA`, `SORPRESA`, `SARCASMO`, `ENOJO`, `TRISTEZA`, `CONFUSIÓN`, `NEUTRAL`, `PENSATIVO`
- `AvatarPose` dataclass: id, emotion, intensity, image_path, name, description
- `AVATAR_POSES`: 20 mock poses — image_path values are placeholders (files don't exist)
- Helper functions: `get_pose_by_id()`, `get_poses_by_emotion()`, `get_pose_by_emotion_and_intensity()`, `get_random_pose()`

**`__init__.py`** — Pydantic schemas:
- `StickerSuggestionRequest` (text, optional keywords[], optional theme)
- `StickerSuggestionResponse` (original_text, suggestions[], total_suggestions, avatar_pose, detected_emotion, generated_image_base64)
- `EmotionDetectionRequest/Response`, `TextAnalysisRequest/Response`, `StickerSuggestion`, `AvatarPoseResponse`

### Key Implementation Notes

- **No ML models** — emotion detection is entirely regex/keyword-based in Spanish
- **Mock avatar assets** — `AVATAR_POSES` image_path fields point to non-existent files; demo image is a plain colored PIL image
- **No environment variables or config files** — all config (CORS `allow_origins=["*"]`, keyword lists, sticker library) is hardcoded
- **No file storage** — images are base64-encoded in API responses

### Mobile React Native (`mobile/`)

Single-screen React Native app (`App.js`). Sends text to backend, displays detected emotion, sticker suggestions, and the rendered speech bubble image.

**Platform-aware API URL:** `localhost:8000` for iOS/Web, `10.0.2.2:8000` for Android emulator.

### Android Keyboard (`android-keyboard/`)

Custom Android IME (`StickerKeyboardService extends InputMethodService`). Full QWERTY keyboard with Spanish layout (ñ, shift/caps-lock, numeric mode) that shows a FAB sticker button while typing.

**Architecture:**
- `StickerKeyboardService` — IME lifecycle, keyboard builder, FAB expand/collapse, sticker insertion
- `SuggestionManager` — parses `/suggest-sticker` and `/generate-image` responses
- `ApiClient` — OkHttp singleton; `HOST` is hardcoded to `http://192.168.1.89:8000/api/v1`

**Key behaviors:**
- Debounces text updates (500 ms) before calling `/suggest-sticker`; skips re-fetch if text hasn't changed
- LRU cache (20 entries) so repeated words don't hit the network again
- Tapping a FAB bubble calls `/generate-image` and inserts the PNG via `InputConnectionCompat.commitContent()` (falls back to `[$emotion]` text if the receiving app doesn't support rich content)
- Sticker PNG files are written to `cacheDir/stickers/` and deleted on each new input field focus

### Mobile Kotlin (`mobile-kotlin/`)

Native Android companion app. See [mobile-kotlin/CLAUDE.md](mobile-kotlin/CLAUDE.md) for full details.

**Architecture:** Single-activity MVVM — `StickerViewModel` (StateFlow) → `MainActivity` (ViewBinding). Calls `/suggest-sticker` then `/generate-image` sequentially.

## Dependencies

### Production (`requirements.txt`)
| Package | Version |
|---------|---------|
| fastapi | 0.104.1 |
| uvicorn[standard] | 0.24.0 |
| pydantic | 2.5.0 |
| pydantic-settings | 2.1.0 |
| python-multipart | 0.0.6 |
| pillow | 10.0.0 |

### Dev (`requirements-dev.txt`)
| Package | Version |
|---------|---------|
| pytest | 7.4.3 |
| pytest-cov | 4.1.0 |
| pytest-asyncio | 0.21.1 |
| black | 23.12.0 |
| flake8 | 6.1.0 |
| mypy | 1.7.1 |
