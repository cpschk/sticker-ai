package com.stickerai.mobile

import android.content.Context

class AppPreferences(context: Context) {
    private val prefs = context.getSharedPreferences("stickerai_prefs", Context.MODE_PRIVATE)

    fun getBackendUrl(): String =
        prefs.getString("backend_url", BuildConfig.DEFAULT_BACKEND_URL)
            ?: BuildConfig.DEFAULT_BACKEND_URL

    fun setBackendUrl(url: String) {
        prefs.edit().putString("backend_url", url).apply()
    }

    fun resetBackendUrl() {
        prefs.edit().remove("backend_url").apply()
    }
}
