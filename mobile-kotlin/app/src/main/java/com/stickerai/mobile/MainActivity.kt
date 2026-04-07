package com.stickerai.mobile

import android.os.Bundle
import android.view.View
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

        binding.btnKeyboardSetup.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Cómo activar el teclado")
                .setMessage(getString(R.string.keyboard_instructions))
                .setPositiveButton("Entendido", null)
                .show()
        }

        lifecycleScope.launch {
            viewModel.uiState.collect { state -> render(state) }
        }
    }

    private fun render(state: StickerUiState) {
        // Loading
        binding.progressBar.visibility = if (state.loading) View.VISIBLE else View.GONE
        binding.btnGenerate.isEnabled = !state.loading
        binding.btnGenerate.text = if (state.loading) "Generando..." else getString(R.string.btn_generate)
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

        // Sticker image
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
