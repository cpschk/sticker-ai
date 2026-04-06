package com.stickerai.keyboard

import android.os.Handler
import android.os.Looper
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Response
import org.json.JSONObject
import java.io.IOException

object SuggestionManager {

    data class StickerResult(
        val emotion: String,
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

    interface ImageCallback {
        fun onImage(base64: String)
        fun onError()
    }

    private val mainHandler = Handler(Looper.getMainLooper())

    /** Obtiene emoción + sugerencias para un texto (sin generar imagen). */
    fun fetchSuggestion(text: String, callback: SuggestionCallback) {
        ApiClient.getSticker(text, object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                mainHandler.post { callback.onError() }
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) {
                        mainHandler.post { callback.onError() }
                        return
                    }
                    runCatching {
                        val json        = JSONObject(response.body!!.string())
                        val emotion     = json.optString("detected_emotion", "")
                        val suggestions = parseSuggestions(json)
                        mainHandler.post { callback.onResult(StickerResult(emotion, suggestions)) }
                    }.onFailure {
                        it.printStackTrace()
                        mainHandler.post { callback.onError() }
                    }
                }
            }
        })
    }

    /** Genera el sticker final (personaje + globo) y devuelve su base64. */
    fun generateImage(text: String, emotion: String, callback: ImageCallback) {
        ApiClient.generateImage(text, emotion, object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                mainHandler.post { callback.onError() }
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) {
                        mainHandler.post { callback.onError() }
                        return
                    }
                    runCatching {
                        val json   = JSONObject(response.body!!.string())
                        val base64 = json.getString("image_base64")
                        mainHandler.post { callback.onImage(base64) }
                    }.onFailure {
                        it.printStackTrace()
                        mainHandler.post { callback.onError() }
                    }
                }
            }
        })
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
