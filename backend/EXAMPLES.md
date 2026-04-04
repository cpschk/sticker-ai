# Ejemplos de Uso - Sticker AI Backend

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
python main.py
```

O con uvicorn:

```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

## Endpoints

### 1. Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "service": "Sticker AI Backend"
}
```

### 2. Analizar Texto (con detección de emociones)

**POST** `/api/v1/analyze-text`

Realiza un análisis completo del texto incluyendo detección de emociones.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "jajaja no puede ser increíble!"
  }'
```

**Respuesta:**
```json
{
  "text": "jajaja no puede ser increíble!",
  "keywords": ["increível", "puede"],
  "sentiment": "positive",
  "theme": "general",
  "emotion": "risa",
  "emotion_intensity": 0.85,
  "emotion_intensity_level": "alta",
  "emotion_confidence": 0.75
}
```

**Parámetros incluidos:**
- `text` - Pequeño análisis del texto
- `keywords` - Palabras clave extraídas
- `sentiment` - Sentimiento general (positive, negative, neutral)
- `theme` - Tema del texto (celebration, love, humor, nature, work, general)
- `emotion` - Emoción detectada (risa, sorpresa, sarcasmo, enojo, tristeza, confusión)
- `emotion_intensity` - Intensidad de la emoción (0.0 - 1.0)
- `emotion_intensity_level` - Nivel cualitativo (baja, media, alta)
- `emotion_confidence` - Confianza en la detección (0.0 - 1.0)

### 3. Detectar Emoción

**POST** `/api/v1/detect-emotion`

Detecta la emoción dominante en un texto.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "jajaja no puede ser increíble!!!"
  }'
```

**Respuesta:**
```json
{
  "emotion": "risa",
  "intensity": 0.85,
  "intensity_level": "alta",
  "confidence": 0.75,
  "all_scores": {
    "risa": 0.75,
    "sorpresa": 0.5,
    "enojo": 0.0,
    "tristeza": 0.0,
    "confusión": 0.0,
    "sarcasmo": 0.0
  }
}
```

#### Emociones soportadas:

- **risa**: Risa y felicidad
  - Keywords: "jajaja", "haha", "lol", "me rio"
  - Ejemplo: `"jajaja qué divertido!!!"`

- **sorpresa**: Sorpresa y asombro
  - Keywords: "no puede ser", "increíble", "wow", "ay dios"
  - Ejemplo: `"no puede ser! increíble!!!"`

- **sarcasmo**: Sarcasmo e ironía
  - Keywords: "claro", "seguro", "te dije", "como si"
  - Ejemplo: `"claro que sí, seguro eso es cierto"`

- **enojo**: Enojo y furia
  - Keywords: "furioso", "rabia", "odio", "maldita"
  - Ejemplo: `"¡¡¡estoy furioso!!!"`

- **tristeza**: Tristeza y dolor
  - Keywords: "triste", "llorar", "dolor", "nunca"
  - Ejemplo: `"Me siento triste, mi corazón duele"`

- **confusión**: Confusión e incertidumbre
  - Keywords: "confundido", "no entiendo", "que", "perdida"
  - Ejemplo: `"No entiendo... ¿qué pasa??"`

### 4. Sugerir Stickers

**POST** `/api/v1/suggest-sticker`

**Request básico:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Happy birthday! Let's celebrate together!"
  }'
```

**Request con parámetros opcionales:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Happy birthday!",
    "theme": "celebration",
    "keywords": ["party", "joy"]
  }'
```

**Respuesta:**
```json
{
  "original_text": "Happy birthday! Let's celebrate together!",
  "suggestions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Party Balloon",
      "description": "Colorful balloons",
      "style": "cartoon",
      "tags": ["celebration", "cartoon", "happy"]
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Confetti",
      "description": "Falling confetti",
      "style": "animated",
      "tags": ["celebration", "animated", "happy"]
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "Cake Slice",
      "description": "Delicious cake",
      "style": "realistic",
      "tags": ["celebration", "realistic"]
    }
  ],
  "total_suggestions": 3
}
```

## Documentación Interactiva

Una vez que la aplicación esté corriendo, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Pruebas de Emociones

```bash
# Ejecutar pruebas del detector de emociones
python test_emotions.py
```

Salida de ejemplo:
```
======================================================================
EMOTION DETECTION TESTS
======================================================================

Text: 'jajaja'
Emotion: RISA
Intensity: 0.85/1.0 (alta)
Confidence: 0.75/1.0
All scores: {'risa': 0.75, 'sorpresa': 0.0, ...}
----------------------------------------------------------------------

Text: 'no puede ser!'
Emotion: SORPRESA
Intensity: 0.65/1.0 (media)
Confidence: 0.5/1.0
All scores: {'sorpresa': 0.5, 'confusión': 0.25, ...}
----------------------------------------------------------------------
```

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py              # Modelos Pydantic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py                # GET /health
│   │   ├── analyze.py               # POST /analyze-text
│   │   ├── emotions.py              # POST /detect-emotion
│   │   └── stickers.py              # POST /suggest-sticker
│   └── services/
│       ├── __init__.py
│       ├── text_analyzer.py         # Análisis de texto
│       ├── emotion_detector.py      # Detección de emociones
│       └── sticker_generator.py     # Generación de stickers
├── main.py                          # Aplicación principal
├── test_emotions.py                 # Pruebas de emociones
├── requirements.txt                 # Dependencias
└── EXAMPLES.md                      # Este archivo
```

## Próximos Pasos

1. **Integración con IA**: Reemplazar la lógica simple de análisis con modelos de IA reales (transformers, BERT)
2. **Base de datos**: Agregar persistencia con PostgreSQL o MongoDB
3. **Autenticación**: Implementar JWT o OAuth2
4. **Caché**: Añadir Redis para caché de resultados
5. **Testing**: Agregar tests unitarios y de integración
6. **Deployment**: Dockerizar la aplicación

