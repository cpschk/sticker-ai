# Deploy en Railway

## Pre-requisitos
- Cuenta en [railway.app](https://railway.app) (free tier disponible)
- Repositorio en GitHub (este monorepo)

## Pasos

### 1. Crear el proyecto en Railway

1. Ir a [railway.app](https://railway.app) → **New Project**
2. Seleccionar **Deploy from GitHub repo**
3. Autorizar acceso y seleccionar este repositorio
4. En la pantalla de configuración, expandir **Advanced** y establecer:
   - **Root Directory**: `backend`
5. Railway detectará el `Procfile` automáticamente y usará:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### 2. Variables de entorno en Railway dashboard

En el panel del servicio → **Variables**, agregar:

| Variable          | Valor para producción          | Descripción                        |
|-------------------|--------------------------------|------------------------------------|
| `ALLOWED_ORIGINS` | `*`                            | CORS origins (restringir en prod)  |
| `BASE_URL`        | `https://<tu-subdominio>.up.railway.app` | URL pública (se conoce tras deploy) |

> Railway inyecta `PORT` automáticamente — no lo agregues manualmente.

### 3. Obtener la URL pública

Una vez desplegado, en el panel del servicio → **Settings** → **Domains**:
- Copiar la URL generada, ej: `https://sticker-ai-backend-production.up.railway.app`

### 4. Actualizar el cliente Android

Editar el archivo:
```
android-keyboard/app/src/main/java/com/stickerai/keyboard/ApiClient.kt
```

Cambiar la línea con `BASE_URL`:
```kotlin
// Antes (LAN local):
private const val BASE_URL = "http://192.168.1.89:8000/api/v1/suggest-sticker"

// Después (Railway):
private const val HOST = "https://sticker-ai-backend-production.up.railway.app"
```

Asegurarse de que todas las referencias a `HOST` en `ApiClient.kt` usen la
nueva URL, sin trailing slash.

### 5. Verificar el deploy

```bash
# Health check
curl https://<tu-subdominio>.up.railway.app/health

# Test suggest-sticker
curl -X POST https://<tu-subdominio>.up.railway.app/api/v1/suggest-sticker \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja esto es gracioso"}'

# Test generate-image
curl -X POST https://<tu-subdominio>.up.railway.app/api/v1/generate-image \
  -H "Content-Type: application/json" \
  -d '{"text": "jajaja", "emotion": "risa"}' | python -m json.tool
```

## Notas sobre el free tier de Railway

- **500 horas/mes** de ejecución gratuita (suficiente para desarrollo)
- El servicio se duerme tras inactividad → primera petición puede tardar ~5s
- Si se necesita que esté siempre activo, configurar un cron de health-check externo
  (ej: [cron-job.org](https://cron-job.org) → GET /health cada 10 minutos)

## Estructura de archivos de deploy

```
backend/
├── Procfile          # Comando de arranque para Railway
├── runtime.txt       # Version de Python (3.11.0)
├── requirements.txt  # Dependencias (incluye python-dotenv)
├── .env.example      # Variables de entorno documentadas
├── .railwayignore    # Archivos excluidos del deploy
├── main.py           # Entrada de la app (lee PORT del entorno)
└── assets/
    └── poses/        # PNGs de avatares por emoción (incluidos en deploy)
```
