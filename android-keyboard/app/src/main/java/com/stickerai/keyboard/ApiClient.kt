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
        .readTimeout(10, TimeUnit.SECONDS)
        .build()

    private const val BASE_URL = "http://192.168.1.89:8000/api/v1/suggest-sticker"

    fun getSticker(text: String, callback: Callback) {
        val body = JSONObject().apply { put("text", text) }
            .toString()
            .toRequestBody(JSON)

        val request = Request.Builder()
            .url(BASE_URL)
            .post(body)
            .build()

        client.newCall(request).enqueue(callback)
    }
}
