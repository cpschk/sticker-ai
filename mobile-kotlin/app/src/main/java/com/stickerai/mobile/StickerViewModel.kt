package com.stickerai.mobile

import android.app.Application
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class StickerViewModel(application: Application) : AndroidViewModel(application) {

    private val prefs = AppPreferences(application)

    private val _uiState = MutableStateFlow(StickerUiState())
    val uiState: StateFlow<StickerUiState> = _uiState.asStateFlow()

    fun generateSticker(text: String) {
        if (text.isBlank()) return

        ApiClient.baseUrl = prefs.getBackendUrl()
        _uiState.value = StickerUiState(loading = true)

        viewModelScope.launch {
            try {
                val (emotion, suggestions) = ApiClient.suggestSticker(text)
                _uiState.value = _uiState.value.copy(emotion = emotion, suggestions = suggestions)

                val base64 = ApiClient.generateImage(text, emotion)
                val bitmap = base64ToBitmap(base64)
                _uiState.value = _uiState.value.copy(loading = false, imageBitmap = bitmap)

            } catch (e: Exception) {
                _uiState.value = StickerUiState(error = e.message ?: "Error desconocido")
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }

    private fun base64ToBitmap(base64: String): Bitmap {
        val bytes = Base64.decode(base64, Base64.DEFAULT)
        return BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
    }
}
