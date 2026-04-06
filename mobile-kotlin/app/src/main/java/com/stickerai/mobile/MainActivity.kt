package com.stickerai.mobile

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.stickerai.mobile.databinding.ActivityMainBinding
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: StickerViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnGenerate.setOnClickListener {
            val text = binding.editText.text.toString().trim()
            if (text.isEmpty()) {
                AlertDialog.Builder(this)
                    .setMessage("Por favor ingresa un texto")
                    .setPositiveButton("OK", null)
                    .show()
                return@setOnClickListener
            }
            viewModel.generateSticker(text)
        }

        lifecycleScope.launch {
            viewModel.uiState.collect { state -> render(state) }
        }
    }

    private fun render(state: StickerUiState) {
        // Loading
        binding.progressBar.visibility = if (state.loading) View.VISIBLE else View.GONE
        binding.btnGenerate.isEnabled = !state.loading
        binding.btnGenerate.text = if (state.loading) "Generando..." else "Generar sticker"
        binding.editText.isEnabled = !state.loading

        // Error
        if (state.error != null) {
            AlertDialog.Builder(this)
                .setTitle("Error")
                .setMessage(state.error)
                .setPositiveButton("OK") { _, _ -> viewModel.clearError() }
                .show()
        }

        // Emotion
        if (state.emotion != null) {
            binding.sectionEmotion.visibility = View.VISIBLE
            binding.textEmotion.text = state.emotion
        } else {
            binding.sectionEmotion.visibility = View.GONE
        }

        // Suggestions
        if (state.suggestions.isNotEmpty()) {
            binding.sectionSuggestions.visibility = View.VISIBLE
            binding.containerSuggestions.removeAllViews()
            state.suggestions.forEach { suggestion ->
                val item = layoutInflater.inflate(R.layout.item_suggestion, binding.containerSuggestions, false)
                item.findViewById<TextView>(R.id.textSuggestionName).text = suggestion.name
                item.findViewById<TextView>(R.id.textSuggestionDesc).text = suggestion.description
                binding.containerSuggestions.addView(item)
            }
        } else {
            binding.sectionSuggestions.visibility = View.GONE
        }

        // Image
        if (state.imageBitmap != null) {
            binding.imagePlaceholder.visibility = View.GONE
            binding.imageSticker.visibility = View.VISIBLE
            binding.imageSticker.setImageBitmap(state.imageBitmap)
        } else if (!state.loading) {
            binding.imagePlaceholder.visibility = View.VISIBLE
            binding.imageSticker.visibility = View.GONE
        }
    }
}
