# Martillazo y Gol FC — V17

## Cambios
- 40 jugadores nuevos: 10 POR, 10 EI, 10 DC, 10 ED. Se integran cartas, jugadores y siluetas de los ZIP entregados.
- 30 mediocampistas preparados recuperados de V16 y 24 defensas existentes.
- Sorteo aleatorio sin repeticiones, con cobertura de los 11 puestos del 4-3-3.
- Modo individual contra IA (puja desde el servidor) y salas públicas con lista actualizable.
- Contador de fichajes = cartas en titular + reservas.
- Suma GRL según los datos del catálogo, corregidos Theo 87, Puyol 91, Terry 89 (267).
- Martillazo al cierre/revelación de cada subasta y música opcional suministrada por el usuario.
- Conserva navegación responsive, pujas persistentes, chat, mercado y resultados.

## Despliegue
1. Subir `backend/`, `frontend/` y este archivo a la raíz del repositorio GitHub.
2. Render: raíz `backend`; build `pip install -r requirements.txt`; start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
3. Vercel: raíz `frontend`, framework Vite; variable `VITE_WS_URL=wss://martillazoygol.onrender.com/ws`; compilar `npm run build`.
4. Esperar ambos despliegues, verificar `/health`, y crear sala nueva.

## Observaciones
- Los ratings de porteros y delanteros centrales sin JSON de catálogo son valores iniciales que deben cotejarse con sus cartas ilustradas antes de considerarlos definitivos.
- La IA es una primera versión heurística, no un modelo entrenado.
- Las salas residen en memoria del servidor; al reiniciarse Render se pierden.
- La música requiere activación del usuario por las políticas de reproducción de navegadores.
- Las pruebas automáticas de sintaxis y sorteo pasaron; el frontend no se pudo compilar en este entorno porque no se completó la instalación de dependencias.
