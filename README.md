# Subasta FC V10 — Mercado y gestión de plantilla

# SUBASTA FC V8 — Defensas completas

Partiendo de V7, se integran 7 laterales derechos (LD) y 7 laterales izquierdos (LI), cada uno con PNG de carta, jugador y silueta. Se conservan los 10 centrales (DFC).

## Ubicación
- `frontend/public/fullbacks/LD/` — 7 laterales derechos
- `frontend/public/fullbacks/LI/` — 7 laterales izquierdos
- `frontend/public/centerbacks/` — 10 centrales
- `backend/players.json` — 14 fichas nuevas con `slotPosition` LI o LD; centrales con `slotPosition` DFC

## Reglas de alineación
El motor mantiene `position: DEF` para la validación de cuatro defensas. La interfaz usa `slotPosition` para colocar a cada lateral en su banda y los centrales exclusivamente en DFC. Las cartas sobrantes permanecen fuera del once. La selección de rondas es aleatoria: no está garantizado que salga un lateral de cada banda en una partida corta.

**Importante:** las medias de los 14 laterales son valores provisionales del catálogo, no extraídos de las cartas. Las ediciones, años y recursos se tomaron de los nombres de los PNG suministrados. Premios individuales aún pendientes de catalogación.

## Ejecución
Backend: `cd backend` y `py -m uvicorn main:app --reload --port 8000`
Frontend: `cd frontend`, `npm install`, `npm run dev`
Compilación: `npm run build` y `npx cap sync android` (requiere proyecto Android generado).

Ver `docs/CAMBIOS_V10.md` para instrucciones de las nuevas transferencias.
