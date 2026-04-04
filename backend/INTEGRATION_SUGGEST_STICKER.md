# Integración: Avatar Poses en /suggest-sticker

## 🎯 Resumen

El endpoint `POST /api/v1/suggest-sticker` ahora retorna **avatar poses reactivas** basadas en la emoción detectada en el texto del usuario.

## ✨ Qué es Nuevo

El endpoint ahora devuelve:

```json
{
  "original_text": "...",
  "detected_emotion": "risa",                    // ← NUEVO
  "avatar_pose": {                               // ← NUEVO
    "id": "pose_003",
    "emotion": "risa",
    "intensity": 1.0,
    "image_path": "/avatars/poses/risa_alta.png",
    "name": "Risa carcajada",
    "description": "Avatar laughing hard"
  },
  "suggestions": [...],
  "total_suggestions": 5
}
```

## 🏗️ Arquitectura de Integración

```
Usuario → Texto
          ↓
   Text Analyzer
   (tema, keywords)
          ↓
   Emotion Detector ←─────┐
   (emoción, intensidad)  │
          ↓                │
   Avatar Pose Selector ──┘ (selecciona pose basada en emoción + intensidad)
          ↓
   Sticker Generator
   (sugerencias)
          ↓
   Respuesta Final
   (stickers + avatar)
```

## 📦 Modelo de Respuesta Actualizado

**Nuevo campo: `AvatarPoseResponse`**

```python
class AvatarPoseResponse(BaseModel):
    """Response model for avatar pose"""
    id: str              # pose_001 a pose_020
    emotion: str         # risa, enojo, tristeza, etc.
    intensity: float     # 0.0 - 1.0
    image_path: str      # /avatars/poses/...
    name: str            # Nombre descriptivo
    description: str     # Descripción
```

**Campo actualizado: `StickerSuggestionResponse`**

```python
class StickerSuggestionResponse(BaseModel):
    original_text: str
    suggestions: List[StickerSuggestion]
    total_suggestions: int
    avatar_pose: Optional[AvatarPoseResponse] = None      # ← NUEVO
    detected_emotion: Optional[str] = None                # ← NUEVO
```

## 🔄 Flujo de Selección de Pose

1. **Detectar Emoción**
   ```python
   emotion_result = detect_emotion(text)
   # Retorna: 
   # {
   #   "emotion": "risa",
   #   "intensity": 0.85,
   #   "confidence": 0.75
   # }
   ```

2. **Seleccionar Pose**
   ```python
   pose = select_best_pose(
       emotion="risa",
       prefer_intensity=0.85
   )
   # Retorna: AvatarPose más cercana a intensidad 0.85
   ```

3. **Convertir a Modelo de Respuesta**
   ```python
   avatar_pose_response = AvatarPoseResponse(
       id=pose.id,
       emotion=pose.emotion,
       intensity=pose.intensity,
       image_path=pose.image_path,
       name=pose.name,
       description=pose.description
   )
   ```

4. **Incluir en Respuesta**
   ```python
   return StickerSuggestionResponse(
       original_text=text,
       suggestions=suggestions,
       total_suggestions=len(suggestions),
       avatar_pose=avatar_pose_response,
       detected_emotion=emotion_result["emotion"]
   )
   ```

## 📝 Cómo Funciona

### Paso a Paso: Ejemplo de "jajaja no puede ser!"

```
INPUT: "jajaja no puede ser increíble!!!"

1️⃣ Text Analysis
   - Keywords: ["puede", "increible"]
   - Sentiment: positive
   - Theme: general

2️⃣ Emotion Detection
   - Emotion: risa (detected)
   - Intensity: 0.85
   - Confidence: 0.75

3️⃣ Avatar Pose Selection
   Available poses for "risa":
   - pose_001: intensity 0.5
   - pose_002: intensity 0.75
   - pose_003: intensity 1.0 ← SELECTED (closest to 0.85)

4️⃣ Sticker Suggestions
   - Party Balloon
   - Confetti
   - (more stickers...)

5️⃣ Response
   {
     "original_text": "...",
     "detected_emotion": "risa",
     "avatar_pose": {
       "id": "pose_003",
       "emotion": "risa",
       "intensity": 1.0,
       "image_path": "/avatars/poses/risa_alta.png",
       "name": "Risa carcajada",
       "description": "Avatar laughing hard"
     },
     "suggestions": [...],
     "total_suggestions": 3
   }
```

## 🧪 Testing

### Ejecutar Tests de Integración

```bash
python test_suggest_sticker_integration.py
```

**Salida incluye:**
- 8 casos de prueba diferentes
- Análisis completo de cada paso
- Respuesta JSON completa
- Resumen de resultados

### Ejemplos CURL

#### Test 1: Risa
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja no puede ser increíble!!!"}'
```
**Esperado:** pose_003 (risa, intensity 1.0)

#### Test 2: Enojo
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "¡¡¡estoy muy enojado!!!"}'
```
**Esperado:** pose_009 (enojo, intensity 1.0)

#### Test 3: Tristeza
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "me siento muy triste..."}'
```
**Esperado:** pose_011 (tristeza, intensity 0.7)

#### Test 4: Sorpresa
```bash
curl -X POST http://localhost:8000/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "no puede ser! ¡increíble!"}'
```
**Esperado:** pose_006 (sorpresa, intensity 1.0)

## 📊 Matrix de Selección de Poses

| Emoción | Pose Baja | Pose Media | Pose Alta |
|---------|-----------|-----------|-----------|
| **Risa** | pose_001 (0.5) | pose_002 (0.75) | pose_003 (1.0) |
| **Sorpresa** | pose_004 (0.4) | pose_005 (0.7) | pose_006 (1.0) |
| **Enojo** | pose_007 (0.3) | pose_008 (0.65) | pose_009 (1.0) |
| **Tristeza** | pose_010 (0.35) | pose_011 (0.7) | pose_012 (1.0) |
| **Confusión** | pose_013 (0.45) | — | pose_014 (0.85) |
| **Sarcasmo** | pose_015 (0.5) | — | pose_016 (0.9) |
| **Neutral** | pose_017 (0.0) | pose_018 (0.2) | — |
| **Pensativo** | pose_019 (0.4) | — | pose_020 (0.8) |

## 🎬 Casos de Uso

### 1. Chatbot con Avatar Reactivo
```python
response = suggest_sticker("¡Feliz cumpleaños!")
# Retorna: risa + pose_002 + stickers de celebración
```

### 2. Interfaz de Usuario
```javascript
// Frontend
const response = await fetch('/api/v1/suggest-sticker', {
    method: 'POST',
    body: JSON.stringify({ text: userInput })
});

const data = await response.json();

// Mostrar avatar
showAvatar(data.avatar_pose.image_path);

// Mostrar stickers
displayStickers(data.suggestions);
```

### 3. Gamification
```python
# Reacción rápida del avatar según emoción
emotion = response.detected_emotion  # "risa"
intensity = response.avatar_pose.intensity  # 1.0

if intensity >= 0.8:
    animation = "FAST"  # Reacción rápida
elif intensity >= 0.5:
    animation = "MEDIUM"
else:
    animation = "SLOW"
```

## 📂 Archivos Modificados

- ✅ `app/models/__init__.py` - Nuevos modelos
- ✅ `app/routes/stickers.py` - Endpoint actualizado
- ✅ `app/services/avatar_service.py` - Servicio de selección
- ✅ `app/models/avatar_pose.py` - Definiciones de poses
- ✅ `README.md` - Documentación actualizada
- ✅ `API_ENDPOINTS.md` - Documentación de endpoints
- ✅ `test_suggest_sticker_integration.py` - Tests

## 🚀 Próximos Pasos

1. **Base de Datos**: Persistir poses y personalizarlas
2. **Animaciones**: Transiciones suaves entre poses
3. **Customización**: Permite a usuarios crear poses
4. **ML Models**: Mejorar detección de emociones
5. **Multi-idioma**: Soportar más idiomas
6. **Caché**: Cachear poses frecuentes

## ✅ Checklist de Integración

- ✅ Crear modelo `AvatarPoseResponse`
- ✅ Actualizar modelo `StickerSuggestionResponse`
- ✅ Integrar detector de emociones en endpoint
- ✅ Integrar selector de poses en endpoint
- ✅ Retornar pose en respuesta
- ✅ Crear tests de integración
- ✅ Documentar endpoint
- ✅ Crear ejemplos CURL
- ✅ Actualizar README

## 📚 Documentación Relacionada

- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Referencia completa de endpoints
- [AVATAR_POSES.md](AVATAR_POSES.md) - Información de poses
- [AVATAR_SELECTION.md](AVATAR_SELECTION.md) - Servicio de selección
- [EMOTION_SERVICE.md](EMOTION_SERVICE.md) - Detector de emociones

## 🎉 Resumen

El endpoint `/suggest-sticker` ahora proporciona una **experiencia completa y reactiva** devolviendo:

1. **Análisis de texto** (keywords, sentimiento, tema)
2. **Detección de emoción** (6 emociones con intensidad)
3. **Avatar reactivo** (20 poses seleccionadas inteligentemente)
4. **Sugerencias de stickers** (personalizadas por tema)

**Todo en una sola llamada API.** 🚀
