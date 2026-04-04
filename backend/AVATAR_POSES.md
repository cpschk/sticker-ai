# Avatar Poses - Guía de Uso

## Descripción

Estructura Python para representar y gestionar poses de avatar con diferentes emociones e intensidades.

## Estructura de Datos

```python
@dataclass
class AvatarPose:
    id: str              # Identificador único (ej: "pose_001")
    emotion: str         # Emoción (risa, sorpresa, enojo, etc.)
    intensity: float     # Intensidad 0.0 - 1.0
    image_path: str      # Ruta a la imagen del avatar
    name: str            # Nombre descriptivo
    description: str     # Descripción
```

## Mock Data: 20 Poses

- **3 poses** para RISA (intensity: 0.5, 0.75, 1.0)
- **3 poses** para SORPRESA (intensity: 0.4, 0.7, 1.0)
- **3 poses** para ENOJO (intensity: 0.3, 0.65, 1.0)
- **3 poses** para TRISTEZA (intensity: 0.35, 0.7, 1.0)
- **2 poses** para CONFUSIÓN (intensity: 0.45, 0.85)
- **2 poses** para SARCASMO (intensity: 0.5, 0.9)
- **2 poses** para NEUTRAL (intensity: 0.0, 0.2)
- **2 poses** para PENSATIVO (intensity: 0.4, 0.8)

## Uso Básico

### Importar

```python
from app.models.avatar_pose import (
    AVATAR_POSES,
    get_pose_by_id,
    get_poses_by_emotion,
    get_pose_by_emotion_and_intensity,
    PoseEmotion,
)
```

### Obtener todas las poses

```python
all_poses = AVATAR_POSES
print(f"Total poses: {len(all_poses)}")  # 20
```

### Obtener pose por ID

```python
pose = get_pose_by_id("pose_001")
# AvatarPose(
#     id="pose_001",
#     emotion="risa",
#     intensity=0.5,
#     image_path="/avatars/poses/risa_baja.png",
#     name="Sonrisa suave",
#     description="Avatar with a gentle smile"
# )

print(pose.name)        # "Sonrisa suave"
print(pose.emotion)     # "risa"
print(pose.intensity)   # 0.5
```

### Obtener todas las poses de una emoción

```python
# Obtener todas las poses de risa
risa_poses = get_poses_by_emotion("risa")
# [AvatarPose(...), AvatarPose(...), AvatarPose(...)]

for pose in risa_poses:
    print(f"{pose.id}: {pose.name} (intensity: {pose.intensity})")

# pose_001: Sonrisa suave (intensity: 0.5)
# pose_002: Risa media (intensity: 0.75)
# pose_003: Risa carcajada (intensity: 1.0)
```

### Encontrar pose más cercana por emoción e intensidad

```python
# Buscar una pose de enojo con intensidad 0.5
best_pose = get_pose_by_emotion_and_intensity("enojo", 0.5)
# Retorna la pose de enojo más cercana a intensidad 0.5

print(best_pose.id)         # "pose_008"
print(best_pose.intensity)  # 0.65
print(best_pose.image_path) # "/avatars/poses/enojo_medio.png"
```

### Convertir a diccionario

```python
pose = get_pose_by_id("pose_001")
pose_dict = pose.to_dict()

# {
#     "id": "pose_001",
#     "emotion": "risa",
#     "intensity": 0.5,
#     "image_path": "/avatars/poses/risa_baja.png",
#     "name": "Sonrisa suave",
#     "description": "Avatar with a gentle smile"
# }
```

## Casos de Uso

### 1. Render Avatar según Emoción Detectada

```python
from app.services.emotion_detector import detect_emotion
from app.models.avatar_pose import get_pose_by_emotion_and_intensity

# Detectar emoción del texto
emotion_result = detect_emotion("jajaja esto es hilariante!!!")

# Obtener pose del avatar
avatar_pose = get_pose_by_emotion_and_intensity(
    emotion=emotion_result["emotion"],
    intensity=emotion_result["intensity"]
)

# Usar la imagen
print(f"Avatar image: {avatar_pose.image_path}")
# Avatar image: /avatars/poses/risa_alta.png
```

### 2. Rotación de Poses en Conversación

```python
from app.models.avatar_pose import get_poses_by_emotion
import random

# Usuario hace varias preguntas divertidas
emotion = "risa"

# Obtener todas las poses de risa
risa_poses = get_poses_by_emotion(emotion)

# Rotar entre diferentes intensidades
for i, message in enumerate(funny_messages):
    # Usar pose diferente cada vez
    pose = risa_poses[i % len(risa_poses)]
    render_avatar(pose.image_path)
    print(message)
```

### 3. Interfaz de Selección de Avatar

```python
from app.models.avatar_pose import AVATAR_POSES

# Listar todas las poses disponibles
print("Available Avatar Poses:")
for pose in AVATAR_POSES:
    emoji = "😄" if pose.emotion == "risa" else "😠"
    print(f"{pose.id}: {emoji} {pose.name}")

# Usuario selecciona: pose_003
selected_pose = AVATAR_POSES[selected_index]
print(f"Selected: {selected_pose.image_path}")
```

### 4. Análisis de Disponibilidad de Poses

```python
from app.models.avatar_pose import AVATAR_POSES

# Contar poses por emoción
emotion_counts = {}
for pose in AVATAR_POSES:
    emotion_counts[pose.emotion] = emotion_counts.get(pose.emotion, 0) + 1

# Encontrar emociones con pocas poses
for emotion, count in emotion_counts.items():
    if count < 3:
        print(f"⚠️ Only {count} pose(s) for {emotion}")
```

## Enumeración de Emociones

```python
from app.models.avatar_pose import PoseEmotion

# Acceder a emociones como enum
for emotion in PoseEmotion:
    print(emotion.value)

# Salida:
# risa
# sorpresa
# sarcasmo
# enojo
# tristeza
# confusión
# neutral
# pensativo
```

## Validation

```python
from app.models.avatar_pose import AvatarPose

# Crear pose con validación
try:
    pose = AvatarPose(
        id="custom_001",
        emotion="risa",
        intensity=1.5,  # ❌ Error: must be 0.0-1.0
        image_path="/path/to/image.png"
    )
except ValueError as e:
    print(f"Error: {e}")
    # Error: Intensity must be between 0.0 and 1.0, got 1.5
```

## Testing

```bash
# Ejecutar demo
python demo_avatar_poses.py

# Salida:
# - Lista de todas las 20 poses
# - Poses organizadas por emoción
# - Ejemplos de búsqueda
# - Ejemplos de conversión a diccionario
```

## API para FastAPI

Si deseas integrar en FastAPI:

```python
from pydantic import BaseModel
from typing import Optional
from app.models.avatar_pose import AvatarPose, get_pose_by_id

# Crear modelo request
class AvatarPoseRequest(BaseModel):
    pose_id: str
    emotion: Optional[str] = None
    intensity: Optional[float] = None

# Crear endpoint
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/avatar-poses/{pose_id}")
async def get_avatar_pose(pose_id: str):
    pose = get_pose_by_id(pose_id)
    if not pose:
        return {"error": "Pose not found"}
    return pose.to_dict()

@router.get("/api/v1/avatar-poses/emotion/{emotion}")
async def get_emotion_poses(emotion: str):
    from app.models.avatar_pose import get_poses_by_emotion
    poses = get_poses_by_emotion(emotion)
    return [pose.to_dict() for pose in poses]
```

## Estructura de Archivos

```
app/
├── models/
│   ├── avatar_pose.py          # ← Estructura y datos
│   └── ...
├── ...

demo_avatar_poses.py            # ← Script de demostración
```

## Extender con Nuevas Poses

```python
from app.models.avatar_pose import AVATAR_POSES, AvatarPose

# Agregar nuevas poses
new_pose = AvatarPose(
    id="pose_021",
    emotion="risa",
    intensity=0.6,
    image_path="/avatars/poses/risa_media_nueva.png",
    name="Nueva sonrisa",
    description="New smile variation"
)

AVATAR_POSES.append(new_pose)
```

## Características

✅ **20 poses mock** listos para usar  
✅ **8 emociones** diferentes  
✅ **Validación** de intensidad  
✅ **Búsqueda flexible** por ID, emoción, intensidad  
✅ **Conversión a diccionario** para JSON  
✅ **Dataclass** para tipo safety  
✅ **Enum** para emociones  
✅ **Funciones helper** para consultas comunes  

## Próximos Pasos

1. Integrar con FastAPI endpoint
2. Conectar con detector de emociones
3. Agregar animaciones entre poses
4. Persistencia en base de datos
5. UI para crear/editar poses
