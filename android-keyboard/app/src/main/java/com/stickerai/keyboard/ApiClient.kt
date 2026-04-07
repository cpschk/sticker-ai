package com.stickerai.keyboard

import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

object ApiClient {

    private val JSON = "application/json; charset=utf-8".toMediaType()

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    // Cambiar BACKEND_URL en app/build.gradle > defaultConfig > buildConfigField
    private const val HOST = BuildConfig.BACKEND_URL

    /** Analiza texto y devuelve emoción + sugerencias (sin imagen). */
    fun getSticker(text: String, callback: Callback) {
        val body = JSONObject().apply { put("text", text) }
            .toString().toRequestBody(JSON)

        client.newCall(
            Request.Builder().url("$HOST/suggest-sticker").post(body).build()
        ).enqueue(callback)
    }

    /** Genera el sticker final (personaje + globo) para un texto y emoción dados. */
    fun generateImage(text: String, emotion: String, callback: Callback) {
        val body = JSONObject().apply {
            put("text", text)
            put("emotion", emotion)
        }.toString().toRequestBody(JSON)

        client.newCall(
            Request.Builder().url("$HOST/generate-image").post(body).build()
        ).enqueue(callback)
    }
}
