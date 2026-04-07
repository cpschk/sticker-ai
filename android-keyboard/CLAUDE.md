# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Build debug APK
./gradlew assembleDebug

# Install on connected device/emulator
./gradlew installDebug

# Run unit tests
./gradlew test

# Run instrumented tests (requires device/emulator)
./gradlew connectedAndroidTest

# Lint
./gradlew lint
```

## Architecture

This is a single-module Android project (`com.stickerai.keyboard`) implementing a custom IME (Input Method Editor). There is no Activity — the entry point is the `StickerKeyboardService` service declared in `AndroidManifest.xml`.

### Components

**`StickerKeyboardService`** (`InputMethodService`) — the entire IME lives here:
- Builds the QWERTY keyboard programmatically at runtime (no `Keyboard`/`KeyboardView` XML); rows are defined as `List<List<String>>` constants at the top of the class.
- `refreshKeyLabels()` updates button text in place without re-inflating views (important for shift/caps-lock performance).
- `onUpdateSelection` is the main text-change hook. It calls `scheduleFetch()` which debounces 500 ms before hitting the backend.
- LRU cache (`LinkedHashMap`, 20 entries) prevents duplicate network calls for the same text.
- `onStartInput` resets shift state, clears the sticker cache directory, and resets `lastFetchedText`.

**`SuggestionManager`** (singleton object) — bridges `ApiClient` and the IME:
- `fetchSuggestion()` calls `/suggest-sticker` → parses `detected_emotion` + `suggestions[]` → posts result to main thread.
- `generateImage()` calls `/generate-image` → returns `image_base64` as a PNG string.
- All callbacks are dispatched on the main thread via `Handler(Looper.getMainLooper())`.

**`ApiClient`** (singleton object) — OkHttp wrapper:
- `HOST` is hardcoded: `http://192.168.1.89:8000/api/v1`. **Change this when the backend IP changes.**
- Timeouts: connect 5 s, read 15 s.

### Sticker insertion flow

1. User types → `onUpdateSelection` → debounce → `fetchWithCache(text)` → `SuggestionManager.fetchSuggestion()` → caches `StickerResult(emotion, suggestions)`.
2. User taps the FAB (top-right corner) → `expandFab()` shows 3 bubble `ImageView`s (all same icon, all carrying the detected `emotion`).
3. User taps a bubble → `generateAndInsertSticker()` → `SuggestionManager.generateImage()` → `insertSticker()`.
4. `tryCommitContent()` writes the PNG to `cacheDir/stickers/`, gets a `FileProvider` URI, and calls `InputConnectionCompat.commitContent()`. Falls back to inserting `[$emotion]` text if the receiving app doesn't declare `image/png` or `image/*` MIME support.

### Layout

`keyboard_view.xml` is a `FrameLayout` with two layers:
1. `LinearLayout` (vertical) — suggestion bar (`HorizontalScrollView`) + `keys_container` (rows added programmatically).
2. `ImageView` FAB + `LinearLayout` `fab_sticker_container` — overlaid at top-right, visibility toggled on expand/collapse.

Key rows use a weight spacer convention: `"_0.5_"` entries in a row list produce invisible `View`s with `weight=0.5` to offset rows (simulates staggered QWERTY layout).

### Key constants (in `StickerKeyboardService.companion`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `DEBOUNCE_MS` | `500L` | Delay before backend call after last keystroke |
| `SHIFT` | `"⇧"` | Shift key token |
| `DELETE` | `"⌫"` | Backspace key token |
| `SPACE` | `"SPACE"` | Space key token |
| `TO_NUM` / `TO_ALPHA` | `"?123"` / `"ABC"` | Mode switch tokens |

### Dependencies

- `androidx.appcompat:appcompat:1.6.1`
- `com.google.android.material:material:1.9.0`
- `com.squareup.okhttp3:okhttp:4.11.0`
- No Retrofit, no ViewModel, no Coroutines — all async is plain OkHttp callbacks marshalled back to the main thread manually.

### Notes

- `minSdk 24`, `targetSdk 33`, `compileSdk 33`.
- `FileProvider` authority: `com.stickerai.keyboard.fileprovider` — defined in `AndroidManifest.xml` and `res/xml/file_paths.xml`. Sticker PNGs are stored under `cacheDir/stickers/` and are deleted on every new `onStartInput`.
- The suggestion bar (`R.id.suggestion_bar`) is present in the layout but currently unused — `updateSuggestionBar()` clears it and delegates display to the FAB bubbles.
