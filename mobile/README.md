# Sticker AI Mobile

App React Native básica para consumir el endpoint `/suggest-sticker` del backend.

## Estructura

- `App.js` - Pantalla única con input de texto, botón y resultado de imagen
- `package.json` - Dependencias Expo
- `app.json` - Configuración Expo
- `babel.config.js` - Configuración de Babel

## Uso

1. Instala dependencias:

```bash
cd mobile
npm install
```

2. Inicia la app:

```bash
npm start
```

3. Ejecuta en emulador o Expo Go.

## Configuración del backend

El código usa esta URL por defecto:

- iOS: `http://localhost:8000/api/v1/suggest-sticker`
- Android: `http://10.0.2.2:8000/api/v1/suggest-sticker`

Ajusta `API_URL` en `App.js` si tu backend corre en otra dirección o dispositivo.

## Funcionalidad

- Input de texto
- Botón `Generar sticker`
- Llama al endpoint `/suggest-sticker`
- Muestra la imagen generada desde `generated_image_base64`
- Muestra emoción y sugerencias
