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
            ?.trim() ?: ""

        updateFabState(hasText = text.isNotEmpty())

        if (text.isEmpty()) return
        // Solo programa fetch si el texto realmente cambió (ignora movimientos de cursor)
        if (text != lastFetchedText) scheduleFetch(text)
    }

    // Se llama cada vez que el usuario toca un campo de texto nuevo
    override fun onStartInput(attribute: android.view.inputmethod.EditorInfo?, restarting: Boolean) {
        super.onStartInput(attribute, restarting)
        if (!restarting) {
            shiftState      = ShiftState.ONE_SHOT
            mode            = Mode.ALPHA
            lastFetchedText = ""
            File(cacheDir, "stickers").listFiles()?.forEach { it.delete() }
            if (keysContainer?.childCount ?: 0 > 0) refreshKeyLabels()
            // Verificar si el campo ya tiene texto (ej: editar un mensaje)
            val existing = currentInputConnection
                ?.getTextBeforeCursor(300, 0)?.toString()?.trim() ?: ""
            updateFabState(hasText = existing.isNotEmpty())
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
            isAllCaps = false   // Android pone allCaps=true por defecto en Button
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
            override fun onError() {
                // Parpadeo rojo único para indicar error de red
                fabSticker?.setColorFilter(0xFFFF4444.toInt())
                debounceHandler.postDelayed({
                    fabSticker?.clearColorFilter()
                }, 600)
            }
        })
    }

    private fun updateSuggestionBar(result: SuggestionManager.StickerResult) {
        suggestionBar?.removeAllViews()
        // suggest-sticker ya no devuelve imágenes; la barra queda vacía.
        if (fabExpanded) {
            buildStickerBubbles(result)
            // Flash de entrada para indicar que los datos reales reemplazaron los placeholders
            val container = fabContainer ?: return
            for (i in 0 until container.childCount) {
                container.getChildAt(i)?.animate()
                    ?.alpha(0f)?.setDuration(0)
                    ?.withEndAction {
                        container.getChildAt(i)?.animate()
                            ?.alpha(1f)?.setDuration(200)?.start()
                    }?.start()
            }
        }
    }

    /**
     * Al tocar una burbuja: llama a /generate-image con el texto actual y la emoción.
     * Atenúa la burbuja mientras carga y, al recibir el PNG, lo inserta en el chat.
     */
    private fun generateAndInsertSticker(bubbleView: ImageView, emotion: String) {
        val text = currentInputConnection
            ?.getTextBeforeCursor(300, 0)?.toString()?.trim()
            ?.takeIf { it.isNotEmpty() } ?: return

        bubbleView.animate().alpha(0.4f).setDuration(150).start()
        bubbleView.isClickable = false

        // Mostrar ícono de carga con rotación continua
        bubbleView.setImageResource(android.R.drawable.ic_popup_sync)
        val spinAnim = ObjectAnimator.ofFloat(bubbleView, "rotation", 0f, 360f).apply {
            duration    = 700
            repeatCount = ObjectAnimator.INFINITE
            interpolator = android.view.animation.LinearInterpolator()
            start()
        }

        SuggestionManager.generateImage(text, emotion, object : SuggestionManager.ImageCallback {
            override fun onImage(base64: String) {
                spinAnim.cancel()
                bubbleView.rotation = 0f
                bubbleView.setImageResource(android.R.drawable.ic_menu_gallery)
                insertSticker(base64, emotion)
                collapseFab()
            }
            override fun onError() {
                spinAnim.cancel()
                bubbleView.rotation = 0f
                bubbleView.setImageResource(android.R.drawable.ic_menu_gallery)
                bubbleView.animate().alpha(1f).setDuration(150).start()
                bubbleView.isClickable = true
            }
        })
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
        val editorInfo = currentInputEditorInfo    ?: return false
        val ic         = currentInputConnection   ?: return false

        // Verificar que el editor acepte image/png.
        // Algunos declaran "image/*" (wildcard) → un PNG siempre califica.
        val mimeTypes = EditorInfoCompat.getContentMimeTypes(editorInfo)
        val canReceive = mimeTypes.any { mime ->
            mime == "image/png" || mime == "image/*" ||
            (mime.endsWith("/*") && "image/png".startsWith(mime.substringBefore("/*")))
        }
        if (!canReceive) return false

        return runCatching {
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
                ic,
                editorInfo,
                contentInfo,
                InputConnectionCompat.INPUT_CONTENT_GRANT_READ_URI_PERMISSION,
                null
            )
        }.getOrDefault(false)
    }

    // ── FAB ───────────────────────────────────────────────────────────────────

    private fun setupFab() {
        updateFabState(hasText = false)  // arranca desactivado
        fabSticker?.setOnClickListener {
            if (!fabEnabled) return@setOnClickListener
            if (fabExpanded) collapseFab()
            else             expandFab()
        }
    }

    private var fabEnabled = false

    private fun updateFabState(hasText: Boolean) {
        if (fabEnabled == hasText) return  // sin cambio, no redibujar
        fabEnabled = hasText
        fabSticker?.apply {
            setBackgroundResource(
                if (hasText) R.drawable.fab_bg else R.drawable.fab_bg_disabled
            )
            animate().scaleX(if (hasText) 1f else 0.85f)
                     .scaleY(if (hasText) 1f else 0.85f)
                     .setDuration(150)
                     .start()
        }
        // Si se desactiva mientras estaba expandido, colapsar
        if (!hasText && fabExpanded) collapseFab()
    }

    private fun expandFab() {
        val container = fabContainer ?: return
        val fab       = fabSticker   ?: return
        val result    = lastFabResult

        container.removeAllViews()
        if (result != null) {
            buildStickerBubbles(result)
        } else {
            // Sin resultado aún: mostrar placeholders y lanzar fetch
            repeat(3) { container.addView(makePlaceholderBubble()) }
            currentInputConnection?.getTextBeforeCursor(300, 0)?.toString()?.trim()
                ?.takeIf { it.isNotEmpty() }?.let { fetchWithCache(it) }
        }

        container.visibility = View.VISIBLE
        fabExpanded = true

        // Rotar el ícono del FAB 45° para indicar "cerrar"
        fab.animate().rotation(45f).setDuration(200).start()

        // Animar entrada de derecha a izquierda con stagger
        // La burbuja más cercana al FAB (última en el layout) entra primero
        val count = container.childCount
        for (i in 0 until count) {
            val child = container.getChildAt(i)
            val translationStart = dp(44 + (count - i) * 12).toFloat()
            child.scaleX       = 0f
            child.scaleY       = 0f
            child.alpha        = 0f
            child.translationX = translationStart
            val delay = (count - 1 - i) * 55L  // la más lejana al FAB entra última
            AnimatorSet().apply {
                playTogether(
                    ObjectAnimator.ofFloat(child, "scaleX",       0f, 1f),
                    ObjectAnimator.ofFloat(child, "scaleY",       0f, 1f),
                    ObjectAnimator.ofFloat(child, "alpha",        0f, 1f),
                    ObjectAnimator.ofFloat(child, "translationX", translationStart, 0f)
                )
                duration     = 240
                startDelay   = delay
                interpolator = OvershootInterpolator(1.8f)
                start()
            }
        }
    }

    private fun collapseFab() {
        val container = fabContainer ?: return
        val fab       = fabSticker   ?: return

        fab.animate().rotation(0f).setDuration(200).start()

        // Animar salida hacia la derecha — la más lejana al FAB sale primero
        val count = container.childCount
        for (i in 0 until count) {
            val child = container.getChildAt(i)
            val translationEnd = dp(44 + (count - i) * 12).toFloat()
            val delay = i * 45L
            child.animate()
                .scaleX(0f).scaleY(0f).alpha(0f)
                .translationX(translationEnd)
                .setDuration(150)
                .setStartDelay(delay)
                .withEndAction { if (i == count - 1) container.visibility = View.GONE }
                .start()
        }
        fabExpanded = false
    }

    /**
     * 3 burbujas idénticas — muestran el ícono del personaje (placeholder).
     * Al tocar → /generate-image → sticker final (gato + globo con texto actual) → chat.
     */
    private fun buildStickerBubbles(result: SuggestionManager.StickerResult) {
        val container = fabContainer ?: return
        container.removeAllViews()
        repeat(3) { container.addView(makeStickerBubble(result.emotion)) }
    }

    private fun makeStickerBubble(emotion: String): ImageView {
        val size = dp(40)
        return ImageView(this).apply {
            setImageResource(android.R.drawable.ic_menu_gallery)
            scaleType     = ImageView.ScaleType.FIT_CENTER
            background    = resources.getDrawable(R.drawable.sticker_bubble_bg, null)
            elevation     = dp(6).toFloat()
            clipToOutline = true
            layoutParams  = LinearLayout.LayoutParams(size, size).apply { setMargins(0, 0, dp(8), 0) }
            setOnClickListener { generateAndInsertSticker(this, emotion) }
        }
    }

    private fun makePlaceholderBubble(): View {
        val size = dp(40)
        return View(this).apply {
            setBackgroundResource(R.drawable.sticker_bubble_bg)
            alpha        = 0.3f
            layoutParams = LinearLayout.LayoutParams(size, size).apply {
                setMargins(0, 0, dp(8), 0)
            }
            // Pulso para indicar carga activa
            ObjectAnimator.ofFloat(this, "alpha", 0.3f, 0.6f).apply {
                duration    = 800
                repeatCount = ObjectAnimator.INFINITE
                repeatMode  = ObjectAnimator.REVERSE
                start()
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
