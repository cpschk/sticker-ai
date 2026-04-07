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

    var baseUrl: String = BuildConfig.DEFAULT_BACKEND_URL

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()

    private fun apiUrl(path: String) = "${baseUrl.trimEnd('/')}/api/v1/$path"

    suspend fun suggestSticker(text: String): Pair<String, List<StickerSuggestion>> =
        withContext(Dispatchers.IO) {
            val body = JSONObject().put("text", text).toString().toRequestBody(JSON_MEDIA_TYPE)
            val request = Request.Builder()
                .url(apiUrl("suggest-sticker"))
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
                .url(apiUrl("generate-image"))
                .post(body)
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
                JSONObject(response.body!!.string()).getString("image_base64")
            }
        }
}
