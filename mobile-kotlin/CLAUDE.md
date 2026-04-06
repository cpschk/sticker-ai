# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Native Android app (Kotlin) for the StickerAI monorepo. Companion to the `backend/` FastAPI service. Users type text, the app calls the backend, and displays detected emotion, sticker suggestions, and a generated speech-bubble image.

## Commands

Build and run via Android Studio or Gradle wrapper:

```bash
# Debug build
./gradlew assembleDebug

# Install on connected device/emulator
./gradlew installDebug

# Run all tests
./gradlew test

# Run instrumented tests (requires emulator or device)
./gradlew connectedAndroidTest

# Lint
./gradlew lint
```

## Architecture

Single-activity app using **MVVM + ViewBinding + Kotlin Coroutines + StateFlow**.

```
app/src/main/java/com/stickerai/mobile/
├── Models.kt          — Data classes: StickerSuggestion, StickerUiState
├── ApiClient.kt       — OkHttp singleton; all network calls (suspend fns, Dispatchers.IO)
├── StickerViewModel.kt — ViewModel; orchestrates API calls, holds StateFlow<StickerUiState>
└── MainActivity.kt    — Single activity; collects StateFlow and calls render()
```

### Data flow

1. User taps "Generar sticker" → `StickerViewModel.generateSticker(text)`
2. ViewModel calls `ApiClient.suggestSticker()` → `POST /api/v1/suggest-sticker` → returns emotion + suggestion list
3. ViewModel calls `ApiClient.generateImage()` → `POST /api/v1/generate-image` → returns base64 PNG
4. ViewModel decodes base64 → `Bitmap`, updates `StickerUiState`
5. `MainActivity.render()` applies the state to views via ViewBinding

### Key implementation notes

- **Backend URL** — hardcoded in `ApiClient.kt`: `http://10.0.2.2:8000/api/v1` (Android emulator loopback to host). Change to your machine's LAN IP when testing on a physical device.
- **No DI framework** — `ApiClient` is a plain `object` singleton; `StickerViewModel` is created by `viewModels()` delegate.
- **Error handling** — any exception in `generateSticker` sets `StickerUiState.error`; `MainActivity` shows an `AlertDialog` and calls `viewModel.clearError()` on dismiss.
- **`/api/v1/generate-image`** — this endpoint does not exist in the current backend; `ApiClient.generateImage()` will always fail. The backend's image is returned inside the `/api/v1/suggest-sticker` response as `generated_image_base64`.

## Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| okhttp3 | 4.11.0 | HTTP client |
| kotlinx-coroutines-android | 1.7.3 | Coroutines |
| lifecycle-viewmodel-ktx | 2.7.0 | ViewModel + viewModelScope |
| lifecycle-runtime-ktx | 2.7.0 | lifecycleScope in Activity |
| activity-ktx | 1.8.2 | `viewModels()` delegate |

compileSdk/targetSdk 34, minSdk 24.
