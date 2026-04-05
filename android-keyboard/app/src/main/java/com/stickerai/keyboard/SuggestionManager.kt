package com.stickerai.keyboard

import android.os.Handler
import android.os.Looper
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Response
import org.json.JSONObject
import java.io.IOException
import java.util.Collections
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger

object SuggestionManager {

    private const val IMAGE_COUNT = 3

    data class StickerResult(
        val emotion: String,
        val images: List<String>,         // hasta IMAGE_COUNT imágenes base64
        val suggestions: List<Suggestion>
    )

    data class Suggestion(
        val id: String,
        val name: String,
        val description: String
    )

    interface SuggestionCallback {
        fun onResult(result: StickerResult)
        fun onError()
    }

    private val mainHandler = Handler(Looper.getMainLooper())

    fun fetchSuggestion(text: String, callback: SuggestionCallback) {
        val images = Collections.synchronizedList(mutableListOf<String>())
        var sharedEmotion = ""
        var sharedSuggestions = emptyList<Suggestion>()
        val metadataCaptured = AtomicBoolean(false)
        val remaining = AtomicInteger(IMAGE_COUNT)

        val tryDeliver: () -> Unit = {
            if (remaining.decrementAndGet() == 0) {
                mainHandler.post {
                    if (images.isEmpty()) callback.onError()
                    else callback.onResult(StickerResult(sharedEmotion, images.toList(), sharedSuggestions))
                }
            }
        }

        repeat(IMAGE_COUNT) {
            ApiClient.getSticker(text, object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    e.printStackTrace()
                    tryDeliver()
                }

                override fun onResponse(call: Call, response: Response) {
                    response.use {
                        if (response.isSuccessful) {
                            runCatching {
                                val json = JSONObject(response.body!!.string())

                                // Capturar emoción y sugerencias solo una vez
                                if (metadataCaptured.compareAndSet(false, true)) {
                                    sharedEmotion = json.optString("detected_emotion", "")
                                    sharedSuggestions = parseSuggestions(json)
                                }

                                val img = json.optString("generated_image_base64", "")
                                if (img.isNotEmpty()) images.add(img)
                            }
                        }
                    }
                    tryDeliver()
                }
            })
        }
    }

    private fun parseSuggestions(json: JSONObject): List<Suggestion> {
        val arr = json.optJSONArray("suggestions") ?: return emptyList()
        return (0 until arr.length()).map { i ->
            arr.getJSONObject(i).let { s ->
                Suggestion(
                    id          = s.optString("id", ""),
                    name        = s.optString("name", ""),
                    description = s.optString("description", "")
                )
            }
        }
    }
}
