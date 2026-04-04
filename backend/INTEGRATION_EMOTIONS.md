# Integración: Detector de Emociones en /analyze-text

## Resumen

El endpoint `POST /api/v1/analyze-text` ahora incluye **detección automática de emociones** junto con el análisis de texto tradicional.

## Cambios Realizados

### 1. Modelo Actualizado

El modelo `TextAnalysisResponse` ahora incluye:

```python
class TextAnalysisResponse(BaseModel):
    # Campos existentes
    text: str
    keywords: List[str]
    sentiment: str
    theme: str
    
    # Nuevos campos de emoción
    emotion: Optional[str]
    emotion_intensity: Optional[float]
    emotion_intensity_level: Optional[str]
    emotion_confidence: Optional[float]
```

### 2. Lógica del Endpoint

El endpoint ahora:
1. Analiza el texto (keywords, tema, sentimiento)
2. Detecta la emoción dominante
3. Retorna ambos resultados combinados

```python
@router.post("/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    # Text analysis
    analyzer = TextAnalyzerService()
    analysis_result = analyzer.analyze(request.text)
    
    # Emotion detection
    emotion_detector = EmotionDetectorService()
    emotion_result = emotion_detector.detect(request.text)
    
    # Combine results
    combined_result = {
        **analysis_result,
        "emotion": emotion_result.get("emotion"),
        "emotion_intensity": emotion_result.get("intensity"),
        "emotion_intensity_level": emotion_result.get("intensity_level"),
        "emotion_confidence": emotion_result.get("confidence"),
    }
    
    return TextAnalysisResponse(**combined_result)
```

## Ejemplos

### Request

```bash
curl -X POST http://localhost:8000/api/v1/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja no puede ser increíble!!!"}'
```

### Response Completo

```json
{
  "text": "jajaja no puede ser increíble!!!",
  "keywords": ["pode", "increíble"],
  "sentiment": "positive",
  "theme": "general",
  "emotion": "risa",
  "emotion_intensity": 0.85,
  "emotion_intensity_level": "alta",
  "emotion_confidence": 0.75
}
```

## Interpretación de Resultados

### Text Analysis (Existente)
- **keywords**: Palabras clave extraídas del texto
- **sentiment**: Sentimiento general (positive, negative, neutral)
- **theme**: Categoría del texto (celebration, love, humor, nature, work, general)

### Emotion Detection (Nuevo)
- **emotion**: Emoción detectada
  - `risa` - Risa y felicidad
  - `sorpresa` - Sorpresa y asombro
  - `sarcasmo` - Sarcasmo e ironía
  - `enojo` - Enojo y furia
  - `tristeza` - Tristeza y dolor
  - `confusión` - Confusión e incertidumbre

- **emotion_intensity**: Intensidad de la emoción (0.0 - 1.0)
  - 0.0 - 0.39: Baja
  - 0.40 - 0.69: Media
  - 0.70 - 1.0: Alta

- **emotion_intensity_level**: Etiqueta cualitativa (baja, media, alta)

- **emotion_confidence**: Confianza en la detección (0.0 - 1.0)

## Casos de Uso

### 1. Análisis Completo de Sentimientos

```python
# Entender tanto el contenido como la emoción
response = POST /api/v1/analyze-text
{
    "text": "me duele mucho el corazón",
    "emotion": "tristeza",
    "sentiment": "negative",
    ...
}
```

### 2. Selección de Stickers Mejorada

```python
# Usar emoción para mejorar sugerencias de stickers
if response.emotion == "risa":
    # Sugerir stickers divertidos
    stickers = get_funny_stickers()
elif response.emotion == "tristeza":
    # Sugerir stickers reconfortantes
    stickers = get_comforting_stickers()
```

### 3. Moderación de Contenido

```python
# Detectar emociones negativas
if response.emotion in ["enojo", "tristeza"]:
    # Ofrecer recursos de ayuda
    show_support_resources()
```

## Compatibilidad

### Endpoint Original `/detect-emotion` (Standalone)

Sigue disponible para detectar **solo emociones** sin análisis de texto:

```bash
POST /api/v1/detect-emotion
{"text": "ejemplo"}
```

Respuesta:
```json
{
  "emotion": "risa",
  "intensity": 0.85,
  "intensity_level": "alta",
  "confidence": 0.75,
  "all_scores": {...}
}
```

## Testing

### Ejecutar Suite de Pruebas

```bash
# Pruebas de integración
python test_integrated_analysis.py

# Pruebas de emociones (standalone)
python test_emotions.py

# Demo interactiva
python demo_emotions.py
```

### Salida Esperada

```
============================================================================
INTEGRATED ANALYSIS TEST - TEXT ANALYSIS WITH EMOTION DETECTION
============================================================================

Test 1:
  📝 Text: 'jajaja esto es hilariante!!!'
  🎭 Emotion: risa (confidence: 0.75)
  💪 Intensity: 0.85/1.0 (alta)
  😊 Sentiment: positive
  📌 Theme: general
  🔑 Keywords: hilariante, esto
  ✅ PASS - Emotion matched
```

## Documentación de API

### Swagger UI

```
http://localhost:8000/docs

# Expandir POST /api/v1/analyze-text
# Ver ejemplo de respuesta con nuevos campos
```

### ReDoc

```
http://localhost:8000/redoc

# Ver modelo TextAnalysisResponse actualizado
```

## Configuración y Personalización

### Ajustar Keywords de Emociones

```python
from app.services.emotion_detector import EmotionDetectorService, Emotion

# Agregar keywords personalizados
EmotionDetectorService.EMOTION_KEYWORDS[Emotion.RISA]["keywords"].extend([
    "divertido", "cómico", "jajajajaja"
])
```

### Cambiar Pesos de Emociones

```python
# Aumentar peso de una emoción
EmotionDetectorService.EMOTION_KEYWORDS[Emotion.ENOJO]["weight"] = 1.2
```

## Próximos Pasos

1. **ML Models**: Reemplazar reglas con modelos entrenados
2. **Multi-idioma**: Soportar más idiomas
3. **Context Analysis**: Análisis contextual mejorado
4. **Caching**: Cachear resultados frecuentes
5. **Analytics**: Registrar y analizar patrones de emociones

## Archivos Modificados

- `app/models/__init__.py` - Actualizado `TextAnalysisResponse`
- `app/routes/analyze.py` - Integración con detector de emociones
- `EXAMPLES.md` - Ejemplos actualizados
- `README.md` - Documentación actualizada
- `test_integrated_analysis.py` - Suite de pruebas de integración

## Soporte

Para problemas o preguntas:
1. Ver [EMOTION_SERVICE.md](EMOTION_SERVICE.md)
2. Ejecutar `python test_integrated_analysis.py`
3. Revisar logs de API en http://localhost:8000/docs
