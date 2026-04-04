# API Endpoints - Sticker AI Backend

## Endpoints Disponibles

### 1. Health Check
```
GET /health
```

### 2. Análisis de Texto (con Emoción)
```
POST /api/v1/analyze-text
```

### 3. Detección de Emoción (Standalone)
```
POST /api/v1/detect-emotion
```

### 4. Sugerencias de Stickers (con Avatar Pose) ⭐ NUEVO
```
POST /api/v1/suggest-sticker
```

---

## 1️⃣ Health Check

**Propósito:** Verificar que la API está activa

**Endpoint:**
```
GET /health
```

**Ejemplo:**
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

---

## 2️⃣ Análisis de Texto

**Propósito:** Análisis completo: keywords, sentimiento, tema y emoción

**Endpoint:**
```
POST /api/v1/analyze-text
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja no puede ser increíble!"}'
```

**Respuesta:**
```json
{
  "text": "jajaja no puede ser increíble!",
  "keywords": ["increible", "puede"],
  "sentiment": "positive",
  "theme": "general",
  "emotion": "risa",
  "emotion_intensity": 0.85,
  "emotion_intensity_level": "alta",
  "emotion_confidence": 0.75
}
```

---

## 3️⃣ Detección de Emoción

**Propósito:** Detectar solo la emoción con todas las puntuaciones

**Endpoint:**
```
POST /api/v1/detect-emotion
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja no puede ser increíble!!!"}'
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

---

## 4️⃣ Sugerir Stickers (con Avatar Pose) ⭐

**Propósito:** Obtener sugerencias de stickers + avatar pose reactivo

**Endpoint:**
```
POST /api/v1/suggest-sticker
```

### Ejemplo 1: Risa

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja no puede ser increíble!!!"}'
```

**Respuesta:**
```json
{
  "original_text": "jajaja no puede ser increíble!!!",
  "detected_emotion": "risa",
  "avatar_pose": {
    "id": "pose_003",
    "emotion": "risa",
    "intensity": 1.0,
    "image_path": "/avatars/poses/risa_alta.png",
    "name": "Risa carcajada",
    "description": "Avatar laughing hard"
  },
  "suggestions": [
    {
      "id": "uuid-1",
      "name": "Party Balloon",
      "description": "Colorful balloons",
      "style": "cartoon",
      "tags": ["general", "cartoon"]
    },
    {
      "id": "uuid-2",
      "name": "Confetti",
      "description": "Falling confetti",
      "style": "animated",
      "tags": ["general", "animated"]
    }
  ],
  "total_suggestions": 2
}
```

### Ejemplo 2: Enojo

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "¡¡¡estoy muy enojado!!!"}'
```

**Respuesta:**
```json
{
  "original_text": "¡¡¡estoy muy enojado!!!",
  "detected_emotion": "enojo",
  "avatar_pose": {
    "id": "pose_009",
    "emotion": "enojo",
    "intensity": 1.0,
    "image_path": "/avatars/poses/enojo_alto.png",
    "name": "Furia extrema",
    "description": "Avatar furious"
  },
  "suggestions": [
    {
      "id": "uuid-3",
      "name": "Rocket",
      "description": "Launching rocket",
      "style": "cartoon",
      "tags": ["work", "cartoon"]
    }
  ],
  "total_suggestions": 1
}
```

### Ejemplo 3: Tristeza

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "me siento muy triste, mi corazón duele..."}'
```

**Respuesta:**
```json
{
  "original_text": "me siento muy triste, mi corazón duele...",
  "detected_emotion": "tristeza",
  "avatar_pose": {
    "id": "pose_011",
    "emotion": "tristeza",
    "intensity": 0.7,
    "image_path": "/avatars/poses/tristeza_media.png",
    "name": "Tristeza moderada",
    "description": "Avatar sad"
  },
  "suggestions": [
    {
      "id": "uuid-4",
      "name": "Heart",
      "description": "Red heart",
      "style": "simple",
      "tags": ["love", "simple"]
    }
  ],
  "total_suggestions": 1
}
```

### Ejemplo 4: Sorpresa

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "no puede ser! ¡increíble! wow!!!"}'
```

**Respuesta:**
```json
{
  "original_text": "no puede ser! ¡increíble! wow!!!",
  "detected_emotion": "sorpresa",
  "avatar_pose": {
    "id": "pose_006",
    "emotion": "sorpresa",
    "intensity": 1.0,
    "image_path": "/avatars/poses/sorpresa_alta.png",
    "name": "Sorpresa extrema",
    "description": "Avatar shocked"
  },
  "suggestions": [
    {
      "id": "uuid-5",
      "name": "Star",
      "description": "Shiny star",
      "style": "simple",
      "tags": ["general", "simple"]
    }
  ],
  "total_suggestions": 1
}
```

### Ejemplo 5: Con Parámetros Opcionales

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{
    "text": "feliz cumpleaños!",
    "theme": "celebration",
    "keywords": ["party", "joy"]
  }'
```

**Respuesta:**
```json
{
  "original_text": "feliz cumpleaños!",
  "detected_emotion": "risa",
  "avatar_pose": {
    "id": "pose_002",
    "emotion": "risa",
    "intensity": 0.75,
    "image_path": "/avatars/poses/risa_media.png",
    "name": "Risa media",
    "description": "Avatar laughing moderately"
  },
  "suggestions": [
    {
      "id": "uuid-6",
      "name": "Cake Slice",
      "description": "Delicious cake",
      "style": "realistic",
      "tags": ["celebration", "realistic", "party"]
    }
  ],
  "total_suggestions": 1
}
```

---

## Estructura de Respuesta del Endpoint /suggest-sticker

```json
{
  "original_text": "string",          // Texto original
  "detected_emotion": "string",       // Emoción detectada (risa, enojo, etc.)
  "avatar_pose": {                    // ⭐ NUEVO: Pose del avatar
    "id": "string",                   // ID de la pose (pose_001-pose_020)
    "emotion": "string",              // Emoción de la pose
    "intensity": 0.0,                 // Intensidad (0.0-1.0)
    "image_path": "string",           // Ruta a imagen del avatar
    "name": "string",                 // Nombre de la pose
    "description": "string"           // Descripción
  },
  "suggestions": [                    // Array de stickers
    {
      "id": "string",                 // ID único del sticker
      "name": "string",               // Nombre del sticker
      "description": "string",        // Descripción
      "style": "string",              // Estilo (cartoon, realistic, etc.)
      "tags": ["string"]              // Array de tags/categorías
    }
  ],
  "total_suggestions": 0              // Cantidad de stickers
}
```

---

## Emociones Soportadas

| Emoción | Keywords | Ejemplo |
|---------|----------|---------|
| **risa** 😄 | jajaja, haha, lol, me rio | "jajaja qué divertido!!!" |
| **sorpresa** 😲 | no puede ser, increíble, wow | "¡no puede ser increíble!" |
| **sarcasmo** 😏 | claro, te dije, seguro | "claro que sí, muy verdad" |
| **enojo** 😠 | furioso, rabia, odio, basta | "¡¡¡estoy furioso!!!" |
| **tristeza** 😢 | triste, llorar, dolor | "me siento triste..." |
| **confusión** 😕 | confundido, no entiendo | "No entiendo..." |

---

## Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `400 Bad Request` - Texto vacío o parámetros inválidos
- `422 Unprocessable Entity` - Modelo de datos inválido
- `500 Internal Server Error` - Error del servidor

---

## Testing desde CLI

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Test 2: Análisis completo
curl -X POST http://localhost:8000/api/v1/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja!"}'

# Test 3: Solo emoción
curl -X POST http://localhost:8000/api/v1/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "¡estoy enojado!"}'

# Test 4: Stickers + Avatar (NUEVO)
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "me duele el corazón"}'
```

---

## Documentación Interactiva

Una vez que la aplicación está corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Resumen de Mejoras

✅ Endpoint `/suggest-sticker` ahora retorna:
- Stickers sugeridos (como antes)
- Emoción detectada (nuevo)
- Avatar pose reactiva (nuevo) ⭐

✅ La pose se selecciona automáticamente basada en:
- Emoción detectada en el texto
- Intensidad de la emoción
- De la lista de 20 poses mock

✅ Totalmente integrado con:
- Detector de emociones
- Selector de poses
- Generador de stickers
