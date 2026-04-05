package com.stickerai.keyboard

import android.animation.AnimatorInflater
import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.ClipDescription
import android.graphics.BitmapFactory
import android.graphics.Typeface
import android.inputmethodservice.InputMethodService
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.util.TypedValue
import android.view.View
import android.view.animation.OvershootInterpolator
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import androidx.core.content.FileProvider
import androidx.core.view.inputmethod.EditorInfoCompat
import androidx.core.view.inputmethod.InputConnectionCompat
import androidx.core.view.inputmethod.InputContentInfoCompat
import java.io.File

class StickerKeyboardService : InputMethodService() {

    // ── Layouts ──────────────────────────────────────────────────────────────

    // Fila 2 lleva medio peso de padding a cada lado para simular el offset QWERTY
    private val alphaRows = listOf(
        listOf("q","w","e","r","t","y","u","i","o","p"),
        listOf("_0.5_","a","s","d","f","g","h","j","k","l","ñ","_0.5_"),
        listOf(SHIFT,"z","x","c","v","b","n","m", DELETE),
        listOf(TO_NUM,",", SPACE,".","↵")
    )

    private val numericRows = listOf(
        listOf("1","2","3","4","5","6","7","8","9","0"),
        listOf("!","@","#","\$","%","^","&","*","(",")"),
        listOf("-","+","=","/",":",";","\"","'","?", DELETE),
        listOf(TO_ALPHA,",", SPACE,".","↵")
    )

    // ── State ─────────────────────────────────────────────────────────────────

    private enum class Mode { ALPHA, NUMERIC }

    /**
     * ONE_SHOT  — mayúscula para la próxima letra, luego vuelve a OFF
     * CAPS_LOCK — mayúsculas hasta que se presione shift de nuevo → OFF
     * OFF       — minúsculas
     */
    private enum class ShiftState { OFF, ONE_SHOT, CAPS_LOCK }

    private var mode       = Mode.ALPHA
    private var shiftState = ShiftState.ONE_SHOT  // arranca en mayúscula (primera letra del campo)
    private var lastShiftMs = 0L                  // timestamp del último tap en shift

    private var suggestionBar: LinearLayout? = null
    private var keysContainer: LinearLayout? = null
    private var fabSticker: ImageView? = null
    private var fabContainer: LinearLayout? = null
    private var fabExpanded = false
    private var lastFabResult: SuggestionManager.StickerResult? = null

    private val debounceHandler = Handler(Looper.getMainLooper())
    private var pendingFetch: Runnable? = null

    // Último texto enviado al backend — evita re-fetch cuando el cursor se mueve sin escribir
    private var lastFetchedText = ""

    // Caché LRU: texto → resultado; máx. 20 entradas
    private val stickerCache = object : LinkedHashMap<String, SuggestionManager.StickerResult>(20, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, SuggestionManager.StickerResult>) = size > 20
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    override fun onCreateInputView(): View {
        val view = layoutInflater.inflate(R.layout.keyboard_view, null)
        suggestionBar  = view.findViewById(R.id.suggestion_bar)
        keysContainer  = view.findViewById(R.id.keys_container)
        fabSticker     = view.findViewById(R.id.fab_sticker)
        fabContainer   = view.findViewById(R.id.fab_sticker_container)
        buildKeyboard()
        setupFab()
        return view
    }

    override fun onUpdateSelection(
        oldSelStart: Int, oldSelEnd: Int,
        newSelStart: Int, newSelEnd: Int,
        candidatesStart: Int, candidatesEnd: Int
    ) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd)
        val text = currentInputConnection
            ?.getTextBeforeCursor(300, 0)
            ?.toString()
            ?.trim()
            ?.takeIf { it.isNotEmpty() } ?: return
        // Solo programa fetch si el texto realmente cambió (ignora movimientos de cursor)
        if (text != lastFetchedText) scheduleFetch(text)
    }

    // Se llama cada vez que el usuario toca un campo de texto nuevo
    override fun onStartInput(attribute: android.view.inputmethod.EditorInfo?, restarting: Boolean) {
        super.onStartInput(attribute, restarting)
        if (!restarting) {
            shiftState = ShiftState.ONE_SHOT  // mayúscula al inicio de cada campo
            mode       = Mode.ALPHA
            refreshKeyLabels()
            // Limpiar PNGs temporales de stickers de sesiones anteriores
            File(cacheDir, "stickers").listFiles()?.forEach { it.delete() }
        }
    }

    override fun onFinishInput() {
        super.onFinishInput()
        pendingFetch?.let { debounceHandler.removeCallbacks(it) }
    }

    // ── Keyboard builder ──────────────────────────────────────────────────────

    private fun buildKeyboard() {
        val container = keysContainer ?: return
        container.removeAllViews()
        val rows = if (mode == Mode.ALPHA) alphaRows else numericRows
        for (row in rows) {
            container.addView(buildRow(row))
        }
    }

    private fun buildRow(keys: List<String>): LinearLayout {
        return LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 2, 0, 2) }
            for (key in keys) {
                addView(if (key.startsWith("_") && key.endsWith("_")) spacer(key) else makeKey(key))
            }
        }
    }

    /** Espaciador invisible para centrar filas (ej: "_0.5_" → weight 0.5) */
    private fun spacer(tag: String): View {
        val w = tag.removeSurrounding("_").toFloatOrNull() ?: 0.5f
        return View(this).apply {
            layoutParams = LinearLayout.LayoutParams(0, 1).apply { weight = w }
        }
    }

    private fun makeKey(key: String): Button {
        val weight  = keyWeight(key)
        val label   = keyLabel(key)
        val special = isSpecial(key)

        return Button(this).apply {
            text = label
            textSize = if (special) 12f else 15f
            typeface = if (special) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
            setPadding(0, 0, 0, 0)
            setTextColor(0xFF1C1C1E.toInt())
            // Fondo con esquinas redondeadas y highlight
            setBackgroundResource(when {
                key == SHIFT && shiftState == ShiftState.ONE_SHOT  -> R.drawable.key_bg          // blanco = activo one-shot
                key == SHIFT && shiftState == ShiftState.CAPS_LOCK -> R.drawable.key_bg          // blanco = caps lock
                special -> R.drawable.key_special_bg
                else    -> R.drawable.key_bg
            })
            // Sombra via elevation
            elevation = dp(3).toFloat()
            // Animación al presionar (escala + sombra)
            stateListAnimator = AnimatorInflater.loadStateListAnimator(
                context, R.animator.key_press
            )
            layoutParams = LinearLayout.LayoutParams(0, dp(44)).apply {
                this.weight = weight
                setMargins(3, 3, 3, 3)
            }
            setOnClickListener { onKey(key) }
        }
    }

    // ── Key press handler ─────────────────────────────────────────────────────

    private fun onKey(key: String) {
        val ic = currentInputConnection ?: return
        when (key) {
            DELETE   -> ic.deleteSurroundingText(1, 0)
            SPACE    -> ic.commitText(" ", 1)
            "↵"      -> {
                ic.performEditorAction(android.view.inputmethod.EditorInfo.IME_ACTION_DONE)
                // Enter dispara fetch inmediato (cancela debounce pendiente)
                triggerFetchNow()
            }
            SHIFT    -> {
                val now = System.currentTimeMillis()
                shiftState = when {
                    shiftState == ShiftState.ONE_SHOT && (now - lastShiftMs) < 400L -> ShiftState.CAPS_LOCK
                    shiftState == ShiftState.CAPS_LOCK -> ShiftState.OFF
                    shiftState == ShiftState.OFF       -> ShiftState.ONE_SHOT
                    else                               -> ShiftState.OFF
                }
                lastShiftMs = now
                refreshKeyLabels()  // solo actualiza texto, no recrea vistas
            }
            TO_NUM   -> { mode = Mode.NUMERIC; buildKeyboard() }
            TO_ALPHA -> { mode = Mode.ALPHA;   buildKeyboard() }
            else -> {
                val upper = shiftState != ShiftState.OFF && mode == Mode.ALPHA
                ic.commitText(if (upper) key.uppercase() else key, 1)
                if (shiftState == ShiftState.ONE_SHOT) {
                    shiftState = ShiftState.OFF
                    refreshKeyLabels()  // solo actualiza texto, no recrea vistas
                }
            }
        }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    /**
     * Actualiza el texto de cada botón existente sin recrear las vistas.
     * Mucho más rápido que buildKeyboard() — sin layout inflation ni GC pressure.
     */
    private fun refreshKeyLabels() {
        val container = keysContainer ?: return
        val rows = if (mode == Mode.ALPHA) alphaRows else numericRows
        for ((rowIdx, rowKeys) in rows.withIndex()) {
            val rowView = container.getChildAt(rowIdx) as? LinearLayout ?: continue
            var childIdx = 0  // índice real en el LinearLayout, incluye spacers
            for (key in rowKeys) {
                if (key.startsWith("_") && key.endsWith("_")) {
                    childIdx++  // el spacer ocupa un hijo real en el layout
                    continue
                }
                val btn = rowView.getChildAt(childIdx++) as? Button ?: continue
                btn.text = keyLabel(key)
                if (key == SHIFT) {
                    btn.setBackgroundResource(
                        if (shiftState != ShiftState.OFF) R.drawable.key_bg
                        else R.drawable.key_special_bg
                    )
                }
            }
        }
    }

    private fun keyLabel(key: String) = when (key) {
        SHIFT -> when (shiftState) {
            ShiftState.OFF       -> "⇧"
            ShiftState.ONE_SHOT  -> "⇧"
            ShiftState.CAPS_LOCK -> "⇪"   // ícono distinto para caps lock
        }
        DELETE   -> "⌫"
        SPACE    -> "espacio"
        TO_NUM   -> "?123"
        TO_ALPHA -> "ABC"
        else -> if (shiftState != ShiftState.OFF && mode == Mode.ALPHA) key.uppercase() else key
    }

    private fun keyWeight(key: String) = when (key) {
        SHIFT, DELETE, TO_NUM, TO_ALPHA -> 1.5f
        SPACE -> 4.0f
        "↵"   -> 1.5f
        else  -> 1.0f
    }

    private fun isSpecial(key: String) =
        key in listOf(SHIFT, DELETE, SPACE, TO_NUM, TO_ALPHA, "↵")

    private fun dp(value: Int) = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_DIP, value.toFloat(), resources.displayMetrics
    ).toInt()

    // ── Suggestion fetch ──────────────────────────────────────────────────────

    /** Programa un fetch diferido (500 ms). Cancela cualquier fetch previo pendiente. */
    private fun scheduleFetch(text: String) {
        pendingFetch?.let { debounceHandler.removeCallbacks(it) }
        pendingFetch = Runnable { fetchWithCache(text) }
            .also { debounceHandler.postDelayed(it, DEBOUNCE_MS) }
    }

    /** Cancela el debounce y ejecuta el fetch de inmediato (usado por Enter). */
    private fun triggerFetchNow() {
        pendingFetch?.let { debounceHandler.removeCallbacks(it) }
        pendingFetch = null
        val text = currentInputConnection
            ?.getTextBeforeCursor(300, 0)
            ?.toString()?.trim()
            ?.takeIf { it.isNotEmpty() } ?: return
        fetchWithCache(text)
    }

    /**
     * Sirve desde caché si el texto ya fue consultado; llama al backend solo si es nuevo.
     * Actualiza [lastFetchedText] para evitar re-fetches duplicados desde onUpdateSelection.
     */
    private fun fetchWithCache(text: String) {
        lastFetchedText = text
        val cached = stickerCache[text]
        if (cached != null) {
            lastFabResult = cached
            updateSuggestionBar(cached)
            return
        }
        SuggestionManager.fetchSuggestion(text, object : SuggestionManager.SuggestionCallback {
            override fun onResult(result: SuggestionManager.StickerResult) {
                stickerCache[text] = result
                lastFabResult = result
                updateSuggestionBar(result)
            }
            override fun onError() { /* fallo silencioso */ }
        })
    }

    private fun updateSuggestionBar(result: SuggestionManager.StickerResult) {
        val bar = suggestionBar ?: return
        bar.removeAllViews()
        result.images.take(3).forEach { base64 ->
            bar.addView(makeStickerImage(base64, result.emotion))
        }
    }

    /** ImageView con la imagen base64 del backend. Al tocarla intenta insertar la imagen. */
    private fun makeStickerImage(base64: String, emotion: String): ImageView {
        val bytes  = Base64.decode(base64, Base64.DEFAULT)
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)

        return ImageView(this).apply {
            setImageBitmap(bitmap)
            scaleType    = ImageView.ScaleType.FIT_CENTER
            elevation    = dp(2).toFloat()
            layoutParams = LinearLayout.LayoutParams(dp(48), dp(48)).apply {
                setMargins(6, 4, 6, 4)
            }
            setOnClickListener { insertSticker(base64, emotion) }
        }
    }

    /**
     * Intenta insertar el sticker como imagen rica (commitContent).
     * Si el campo de texto receptor no soporta imágenes, inserta texto de fallback.
     */
    private fun insertSticker(base64: String, emotion: String) {
        if (!tryCommitContent(base64, emotion)) {
            currentInputConnection?.commitText("[$emotion]", 1)
        }
    }

    /**
     * Guarda el PNG en caché y lo inserta vía InputConnectionCompat.commitContent().
     * Funciona en apps que declaran soporte para imágenes (WhatsApp, Telegram, etc.).
     * Devuelve true si el insert fue aceptado, false si el editor no lo soporta.
     */
    private fun tryCommitContent(base64: String, emotion: String): Boolean {
        val editorInfo = currentInputEditorInfo ?: return false

        // Verificar que el editor acepte image/png o image/*
        val mimeTypes = EditorInfoCompat.getContentMimeTypes(editorInfo)
        val canReceive = mimeTypes.any { it == "image/png" || it == "image/*" }
        if (!canReceive) return false

        return runCatching {
            // Escribir PNG temporal en caché interna
            val dir  = File(cacheDir, "stickers").also { it.mkdirs() }
            val file = File(dir, "sticker_${System.currentTimeMillis()}.png")
            file.writeBytes(Base64.decode(base64, Base64.DEFAULT))

            val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file)
            val contentInfo = InputContentInfoCompat(
                uri,
                ClipDescription(emotion, arrayOf("image/png")),
                null
            )
            InputConnectionCompat.commitContent(
                currentInputConnection!!,
                editorInfo,
                contentInfo,
                InputConnectionCompat.INPUT_CONTENT_GRANT_READ_URI_PERMISSION,
                null
            )
        }.getOrDefault(false)
    }

    // ── FAB ───────────────────────────────────────────────────────────────────

    private fun setupFab() {
        fabSticker?.setOnClickListener {
            if (fabExpanded) collapseFab()
            else             expandFab()
        }
    }

    private fun expandFab() {
        val container = fabContainer ?: return
        val fab       = fabSticker   ?: return
        val result    = lastFabResult

        // Construir burbujas con el último resultado; si aún no hay, pedir al backend
        container.removeAllViews()
        if (result != null && result.images.isNotEmpty()) {
            buildStickerBubbles(result)
        } else {
            // Sin resultados todavía — lanza fetch del texto actual
            val text = currentInputConnection
                ?.getTextBeforeCursor(300, 0)
                ?.toString()?.trim()
                ?.takeIf { it.isNotEmpty() }
            if (text != null) {
                fetchWithCache(text)
                // Muestra indicador vacío mientras carga
                buildStickerBubbles(SuggestionManager.StickerResult("", emptyList(), emptyList()))
            }
        }

        container.visibility = View.VISIBLE
        fabExpanded = true

        // Rotar el ícono del FAB 45° para indicar "cerrar"
        fab.animate().rotation(45f).setDuration(200).start()

        // Animar entrada de cada burbuja con stagger
        for (i in 0 until container.childCount) {
            val child = container.getChildAt(i)
            child.scaleX = 0f
            child.scaleY = 0f
            child.alpha  = 0f
            val delay = i * 60L
            AnimatorSet().apply {
                playTogether(
                    ObjectAnimator.ofFloat(child, "scaleX", 0f, 1f),
                    ObjectAnimator.ofFloat(child, "scaleY", 0f, 1f),
                    ObjectAnimator.ofFloat(child, "alpha",  0f, 1f)
                )
                duration    = 220
                startDelay  = delay
                interpolator = OvershootInterpolator(2f)
                start()
            }
        }
    }

    private fun collapseFab() {
        val container = fabContainer ?: return
        val fab       = fabSticker   ?: return

        fab.animate().rotation(0f).setDuration(200).start()

        // Animar salida en orden inverso
        val count = container.childCount
        for (i in count - 1 downTo 0) {
            val child = container.getChildAt(i)
            val delay = (count - 1 - i) * 50L
            child.animate()
                .scaleX(0f).scaleY(0f).alpha(0f)
                .setDuration(150)
                .setStartDelay(delay)
                .withEndAction { if (i == 0) container.visibility = View.GONE }
                .start()
        }
        fabExpanded = false
    }

    /** Crea los ImageView circulares dentro del contenedor del FAB. */
    private fun buildStickerBubbles(result: SuggestionManager.StickerResult) {
        val container = fabContainer ?: return
        container.removeAllViews()

        val images = result.images.take(3)

        if (images.isEmpty()) {
            // Placeholder animado mientras carga
            repeat(3) {
                container.addView(makePlaceholderBubble())
            }
            return
        }

        images.forEachIndexed { idx, base64 ->
            container.addView(makeStickerBubble(base64, result.emotion, idx))
        }
    }

    private fun makeStickerBubble(base64: String, emotion: String, index: Int): ImageView {
        val bytes  = Base64.decode(base64, Base64.DEFAULT)
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        val size   = dp(52)

        return ImageView(this).apply {
            setImageBitmap(bitmap)
            scaleType    = ImageView.ScaleType.CENTER_CROP
            background   = resources.getDrawable(R.drawable.sticker_bubble_bg, null)
            elevation    = dp(6).toFloat()
            clipToOutline = true
            layoutParams = LinearLayout.LayoutParams(size, size).apply {
                setMargins(0, 0, 0, dp(6))
            }
            setOnClickListener {
                insertSticker(base64, emotion)
                collapseFab()
            }
        }
    }

    private fun makePlaceholderBubble(): View {
        val size = dp(52)
        return View(this).apply {
            setBackgroundResource(R.drawable.sticker_bubble_bg)
            alpha        = 0.4f
            layoutParams = LinearLayout.LayoutParams(size, size).apply {
                setMargins(0, 0, 0, dp(6))
            }
        }
    }

    companion object {
        private const val DEBOUNCE_MS = 500L
        private const val SHIFT    = "⇧"
        private const val DELETE   = "⌫"
        private const val SPACE    = "SPACE"
        private const val TO_NUM   = "?123"
        private const val TO_ALPHA = "ABC"
    }
}
