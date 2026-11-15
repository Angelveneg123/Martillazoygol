# Subasta FC V11 — Responsive

- Navegación inferior fija en móviles: Subasta, Mi XI y mercado, Chat.
- Chat oculto en otras vistas móviles para evitar desplazamientos largos.
- Carta misteriosa y controles de puja compactos.
- Campo 4-3-3 ajustado a pantallas de 320–430 px; cartas y reservas adaptadas.
- Se mantiene la presentación de escritorio y la lógica FastAPI/WebSocket de V10.
- No se ha validado aún en dispositivos Android reales ni compilado APK.

Para ejecutar: backend `py -m uvicorn main:app --reload --port 8000`; frontend `npm install` y `npm run dev`.
