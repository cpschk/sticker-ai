package com.stickerai.mobile

import android.graphics.Bitmap

data class StickerSuggestion(
    val id: String,
    val name: String,
    val description: String
)

data class StickerUiState(
    val loading: Boolean = false,
    val emotion: String? = null,
    val suggestions: List<StickerSuggestion> = emptyList(),
    val imageBitmap: Bitmap? = null,
    val error: String? = null
)
