#!/usr/bin/env python3
"""
Quick example: Using the speech bubble image manipulation service
"""

from app.services.image_manipulation import (
    add_speech_bubble,
    ImageWithSpeechBubble,
    SpeechBubbleStyle
)


# ============================================================================
# EJEMPLO 1: USO MÁS SIMPLE
# ============================================================================

print("EJEMPLO 1: Uso simple")
print("-" * 50)

# Solo 3 líneas necesarias
img = add_speech_bubble(
    "avatar.png",              # Imagen de entrada
    "¡Hola mundo!"            # Texto
)
img.save("result_1.png")       # Guardar resultado

print("✓ Imagen creada: result_1.png")
print()


# ============================================================================
# EJEMPLO 2: CON GUARDADO DIRECTO
# ============================================================================

print("EJEMPLO 2: Con guardado automático")
print("-" * 50)

img = add_speech_bubble(
    "avatar.png",
    "Este globo se guarda automáticamente",
    output_path="result_2.png"     # Se guarda automáticamente
)

print("✓ Imagen guardada: result_2.png")
print()


# ============================================================================
# EJEMPLO 3: CON ESTILO PERSONALIZADO
# ============================================================================

print("EJEMPLO 3: Con estilo personalizado")
print("-" * 50)

# Definir estilo
style = SpeechBubbleStyle(
    bubble_color=(255, 200, 100),      # Naranja
    text_color=(0, 0, 0),              # Negro
    border_color=(200, 100, 0),        # Naranja oscuro
    border_width=3,                    # Borde grueso
    padding=20                         # Espacio interno
)

# Usar estilo
img = ImageWithSpeechBubble.add_speech_bubble(
    "avatar.png",
    "¡Con estilo personalizado!",
    output_path="result_3.png",
    style=style,
    bubble_position="top",
    font_size=20
)

print("✓ Imagen con estilo: result_3.png")
print()


# ============================================================================
# EJEMPLO 4: MÚLTIPLES ESTILOS
# ============================================================================

print("EJEMPLO 4: Múltiples estilos según emoción")
print("-" * 50)

# Definir estilos por emoción
emotion_styles = {
    "feliz": SpeechBubbleStyle(
        bubble_color=(255, 255, 100),      # Amarillo
        border_color=(200, 150, 0)
    ),
    "enojado": SpeechBubbleStyle(
        bubble_color=(255, 150, 150),      # Rojo
        border_color=(200, 0, 0)
    ),
    "triste": SpeechBubbleStyle(
        bubble_color=(150, 200, 255),      # Azul
        border_color=(0, 0, 200)
    ),
}

# Crear imágenes con diferentes estilos
reactions = [
    ("¡Estoy feliz!", "feliz"),
    ("¡Estoy enojado!", "enojado"),
    ("Estoy triste...", "triste")
]

for text, emotion in reactions:
    style = emotion_styles[emotion]
    img = ImageWithSpeechBubble.add_speech_bubble(
        "avatar.png",
        text,
        output_path=f"result_emotion_{emotion}.png",
        style=style
    )
    print(f"  ✓ result_emotion_{emotion}.png")

print()


# ============================================================================
# EJEMPLO 5: CON INTEGRACIÓN DE DETECTOR DE EMOCIONES
# ============================================================================

print("EJEMPLO 5: Integración con detector de emociones")
print("-" * 50)

# Importar detector
from app.services.emotion_detector import detect_emotion

# Función para crear avatar reactivo
def crear_avatar_reactivo(imagen, texto):
    """Crea un avatar con globo reactivo según la emoción detectada"""
    
    # Detectar emoción
    resultado = detect_emotion(texto)
    emocion = resultado.get("emotion", "neutral")
    
    # Mapeo de emociones a colores
    colores = {
        "risa": (255, 255, 100),          # Amarillo
        "sorpresa": (255, 180, 255),      # Magenta
        "enojo": (255, 150, 150),         # Rojo
        "tristeza": (150, 200, 255),      # Azul
        "confusión": (200, 150, 255),     # Púrpura
        "sarcasmo": (200, 200, 200),      # Gris
    }
    
    # Crear estilo con color de emoción
    color = colores.get(emocion, (200, 200, 200))
    style = SpeechBubbleStyle(
        bubble_color=color,
        border_color=tuple(max(0, c-50) for c in color)
    )
    
    # Crear imagen
    return ImageWithSpeechBubble.add_speech_bubble(
        imagen,
        texto,
        style=style
    )

# Usar
textos_ejemplo = [
    "jajaja esto es hilariante!!!",
    "¡no puede ser increíble!",
    "¡¡¡estoy furioso!!!"
]

print("Creando avatares reactivos...")
for i, texto in enumerate(textos_ejemplo):
    img = crear_avatar_reactivo("avatar.png", texto)
    img.save(f"result_reactivo_{i}.png")
    print(f"  ✓ result_reactivo_{i}.png")

print()


# ============================================================================
# EJEMPLO 6: CONFIGURACIÓN AVANZADA
# ============================================================================

print("EJEMPLO 6: Configuración avanzada")
print("-" * 50)

# Estilo muy personalizado
style_avanzado = SpeechBubbleStyle(
    bubble_color=(220, 240, 255),              # Azul claro
    text_color=(20, 40, 100),                  # Azul oscuro
    border_color=(0, 100, 200),                # Azul medio
    border_width=4,                            # Borde grueso
    padding=25,                                # Mucho espacio
    corner_radius=20,                          # Esquinas muy redondeadas
    tail_size=20,                              # Punta grande
    tail_position="bottom-left"                # Punta abajo izquierda
)

# Usar con texto largo
texto_largo = """Este es un ejemplo de texto largo que 
se envolverá automáticamente en varias líneas
para caber perfectamente dentro del globo."""

img = ImageWithSpeechBubble.add_speech_bubble(
    "avatar.png",
    texto_largo,
    output_path="result_avanzado.png",
    style=style_avanzado,
    bubble_position="top",
    font_size=18
)

print("✓ Imagen avanzada: result_avanzado.png")
print()


# ============================================================================
# RESUMEN
# ============================================================================

print("=" * 50)
print("RESUMEN DE EJEMPLOS GENERADOS")
print("=" * 50)

ejemplos = [
    ("result_1.png", "Uso simple básico"),
    ("result_2.png", "Con guardado automático"),
    ("result_3.png", "Con estilo personalizado (naranja)"),
    ("result_emotion_feliz.png", "Estilo feliz (amarillo)"),
    ("result_emotion_enojado.png", "Estilo enojado (rojo)"),
    ("result_emotion_triste.png", "Estilo triste (azul)"),
    ("result_reactivo_0.png", "Avatar reactivo (risa)"),
    ("result_reactivo_1.png", "Avatar reactivo (sorpresa)"),
    ("result_reactivo_2.png", "Avatar reactivo (enojo)"),
    ("result_avanzado.png", "Configuración avanzada"),
]

for archivo, descripcion in ejemplos:
    print(f"  • {archivo:30} - {descripcion}")

print()
print("=" * 50)
print("✨ Todos los ejemplos están listos para usar")
print("=" * 50)
