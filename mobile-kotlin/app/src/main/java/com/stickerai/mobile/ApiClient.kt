package com.stickerai.mobile

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

object ApiClient {

    // Para emulador Android usa 10.0.2.2. Para dispositivo físico, cambia a la IP de tu PC.
    private const val BASE_URL = "http://192.168.1.89:8000/api/v1"

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()

    suspend fun suggestSticker(text: String): Pair<String, List<StickerSuggestion>> =
        withContext(Dispatchers.IO) {
            val body = JSONObject().put("text", text).toString().toRequestBody(JSON_MEDIA_TYPE)
            val request = Request.Builder()
                .url("$BASE_URL/suggest-sticker")
                .post(body)
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
                val json = JSONObject(response.body!!.string())
                val emotion = json.optString("detected_emotion", "")
                val array = json.optJSONArray("suggestions")
                val suggestions = if (array != null) {
                    (0 until array.length()).map { i ->
                        val s = array.getJSONObject(i)
                        StickerSuggestion(
                            id = s.optString("id", i.toString()),
                            name = s.optString("name", ""),
                            description = s.optString("description", "")
                        )
                    }
                } else emptyList()
                Pair(emotion, suggestions)
            }
        }

    suspend fun generateImage(text: String, emotion: String): String =
        withContext(Dispatchers.IO) {
            val body = JSONObject()
                .put("text", text)
                .put("emotion", emotion)
                .toString()
                .toRequestBody(JSON_MEDIA_TYPE)
            val request = Request.Builder()
                .url("$BASE_URL/generate-image")
                .post(body)
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
                JSONObject(response.body!!.string()).getString("image_base64")
            }
        }
}
