package com.stickerai.mobile

import android.os.Bundle
import android.text.InputType
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
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

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == R.id.action_settings) {
            showSettingsDialog()
            return true
        }
        return super.onOptionsItemSelected(item)
    }

    private fun showSettingsDialog() {
        val prefs = AppPreferences(this)
        val editText = EditText(this).apply {
            setText(prefs.getBackendUrl())
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
            hint = "http://192.168.1.89:8000"
        }
        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            val px = (20 * resources.displayMetrics.density).toInt()
            setPadding(px, px / 2, px, 0)
            addView(editText)
        }

        AlertDialog.Builder(this)
            .setTitle("URL del backend")
            .setView(container)
            .setPositiveButton("Guardar") { _, _ ->
                val url = editText.text.toString().trimEnd('/')
                if (url.isNotBlank()) prefs.setBackendUrl(url)
            }
            .setNeutralButton("Restaurar default") { _, _ ->
                prefs.resetBackendUrl()
            }
            .setNegativeButton("Cancelar", null)
            .show()
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
