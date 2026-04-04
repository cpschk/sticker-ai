# Sticker AI Backend

Backend en Python con FastAPI para el sistema de generación de stickers AI.

## Características

✅ Estructura modular y escalable  
✅ Análisis de texto automático  
✅ **Detección de emociones** (6 tipos)  
✅ **Selección inteligente de poses de avatar** selon on emotion  
✅ **Generación de imágenes con globos de diálogo** (Pillow)  
✅ Generación de sugerencias de stickers  
✅ Cheque de salud  
✅ Validación de modelos con Pydantic  
✅ CORS habilitado  
✅ Documentación interactiva (Swagger, ReDoc)  

## Requisitos

- Python 3.8+
- pip

## Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la aplicación
python main.py
```

La API estará disponible en **http://localhost:8000**

## Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Ejemplos de uso**: Ver [EXAMPLES.md](EXAMPLES.md)
- **Detección de emociones**: Ver [EMOTION_SERVICE.md](EMOTION_SERVICE.md)
- **Avatar poses**: Ver [AVATAR_POSES.md](AVATAR_POSES.md)
- **Selección de poses**: Ver [AVATAR_SELECTION.md](AVATAR_SELECTION.md)
- **Manipulación de imágenes**: Ver [IMAGE_MANIPULATION.md](IMAGE_MANIPULATION.md) 🆕
- **Ejemplos de globos de diálogo**: Ver [example_speech_bubbles.py](example_speech_bubbles.py) 🆕

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Verificar salud de la API |
| POST | `/api/v1/analyze-text` | Analizar texto + **detectar emoción** |
| POST | `/api/v1/detect-emotion` | Detectar emoción en texto (standalone) |
| POST | `/api/v1/suggest-sticker` | Obtener stickers + **avatar pose reactivo** ⭐ |

## Emociones Detectadas

🎭 El servicio detecta 6 emociones:
- **😄 risa** - Risa y felicidad
- **😲 sorpresa** - Sorpresa y asombro
- **😏 sarcasmo** - Sarcasmo e ironía
- **😠 enojo** - Enojo y furia
- **😢 tristeza** - Tristeza y dolor
- **😕 confusión** - Confusión e incertidumbre

## 🖼️ Manipulación de Imágenes

El sistema puede agregar **globos de diálogo personalizados** a imágenes usando Pillow:

```python
from app.services.image_manipulation import add_speech_bubble, SpeechBubbleStyle

# Uso simple
img = add_speech_bubble("avatar.png", "¡Hola mundo!")
img.save("result.png")

# Con estilo personalizado
style = SpeechBubbleStyle(
    bubble_color=(255, 255, 100),      # Color del globo
    text_color=(0, 0, 0),              # Color del texto
    border_color=(200, 100, 0),        # Color del borde
    border_width=3
)

img = add_speech_bubble(
    "avatar.png",
    "Texto personalizado",
    output_path="result.png",
    style=style,
    bubble_position="top"
)

img.save("result.png")
```

**Características:**
- ✅ Envoltura de texto automática
- ✅ Estilos personalizables (colores, bordes, esquinas)
- ✅ Posicionamiento flexible (arriba/abajo/izquierda/derecha)
- ✅ Carga de fuentes (DejaVu, Arial, Helvetica)
- ✅ Manejo de RGBA/RGB
- ✅ Integración con detector de emociones

Ver [example_speech_bubbles.py](example_speech_bubbles.py) para 6 ejemplos prácticos.

## Estructura

```
app/
├── models/              # Modelos Pydantic
├── routes/              # Endpoints
│   ├── emotions.py      # Endpoint de emociones
│   └── ...
└── services/            # Lógica de negocio
    ├── emotion_detector.py
    └── ...
```

## Scripts de Demostración

```bash
# Ejemplos de detección de emociones
python demo_emotions.py

# Ejemplos de selección de poses de avatar
python demo_avatar_poses.py
python demo_avatar_selection.py

# Ejemplos de globos de diálogo 🆕
python demo_speech_bubbles.py

# Pruebas
python test_emotions.py
python test_integrated_analysis.py
```

## Desarrollo

```bash
# Con auto-reload
uvicorn main:app --reload --port 8000

# O con Python
python main.py
```
