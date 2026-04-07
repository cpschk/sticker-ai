# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Native Android app (Kotlin) for the StickerAI monorepo. Companion to the `backend/` FastAPI service. Users type text, the app calls the backend, and displays detected emotion, sticker suggestions, and a generated speech-bubble image.

## Commands

Build and run via Android Studio or Gradle wrapper (use `gradlew.bat` on Windows):

```bash
# Debug build
./gradlew assembleDebug

# Install on connected device/emulator
./gradlew installDebug

# Run unit tests
./gradlew test

# Run a single test class
./gradlew test --tests "com.stickerai.mobile.SomeTest"

# Run instrumented tests (requires emulator or device)
./gradlew connectedAndroidTest

# Lint
./gradlew lint
```

## Architecture

Single-activity app using **MVVM + ViewBinding + Kotlin Coroutines + StateFlow**.

```
app/src/main/java/com/stickerai/mobile/
├── Models.kt           — Data classes: StickerSuggestion, StickerUiState
├── ApiClient.kt        — OkHttp singleton; all network calls (suspend fns, Dispatchers.IO)
├── StickerViewModel.kt — ViewModel; orchestrates API calls, holds StateFlow<StickerUiState>
└── MainActivity.kt     — Single activity; collects StateFlow and calls render()
```

### Data flow

1. User taps "Generar sticker" → `StickerViewModel.generateSticker(text)`
2. ViewModel calls `ApiClient.suggestSticker()` → `POST /api/v1/suggest-sticker` → returns emotion + suggestion list
3. ViewModel calls `ApiClient.generateImage()` → `POST /api/v1/generate-image` → returns base64 PNG
4. ViewModel decodes base64 → `Bitmap`, updates `StickerUiState`
5. `MainActivity.render()` applies the state to views via ViewBinding — suggestions are inflated from `item_suggestion.xml` into a `LinearLayout` (no RecyclerView/adapter)

### Key implementation notes

- **Backend URL** — hardcoded in `ApiClient.kt` as `BASE_URL = "http://192.168.1.89:8000/api/v1"`. Change to `10.0.2.2:8000` for Android emulator or your machine's LAN IP for physical device.
- **JSON parsing** — uses `org.json.JSONObject` directly; no Gson/Moshi/kotlinx.serialization. Responses are parsed field-by-field in `ApiClient`.
- **No DI framework** — `ApiClient` is a plain `object` singleton; `StickerViewModel` is created by `viewModels()` delegate.
- **Error handling** — any exception in `generateSticker` sets `StickerUiState.error`; `MainActivity` shows an `AlertDialog` and calls `viewModel.clearError()` on dismiss.
- **`/api/v1/generate-image` is broken** — this endpoint does not exist in the current backend. `ApiClient.generateImage()` will always throw. The sticker image is actually returned inside the `/api/v1/suggest-sticker` response as `generated_image_base64` (currently unused by the app).

## Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| okhttp3 | 4.11.0 | HTTP client |
| kotlinx-coroutines-android | 1.7.3 | Coroutines |
| lifecycle-viewmodel-ktx | 2.7.0 | ViewModel + viewModelScope |
| lifecycle-runtime-ktx | 2.7.0 | lifecycleScope in Activity |
| activity-ktx | 1.8.2 | `viewModels()` delegate |

compileSdk/targetSdk 34, minSdk 24, JVM target 1.8.
