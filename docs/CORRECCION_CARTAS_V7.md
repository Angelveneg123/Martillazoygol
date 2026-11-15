# Corrección de cartas de centrales — V7

Se reemplazaron las diez cartas de defensas centrales por los PNG entregados en `SUBASTA_FC_10_CARTAS_CENTRALES_CORREGIDAS.zip`.

- Cada jugador del catálogo dispone de `cardImage` que apunta a un PNG existente.
- John Terry utiliza la carta edición 2012 y Ronald Araújo la edición 2023, tal como figuran en los archivos entregados.
- Se conservaron las fotografías y siluetas originales de V6. **Atención:** los archivos de fotografía y silueta de Terry y Araújo conservan en su ruta los años anteriores; deben revisarse visualmente para asegurar coherencia con la edición de las cartas.
- No se alteraron las medias, ni las reglas de subasta, ni el chat.

## Inicio

Backend: `cd backend` y `py -m uvicorn main:app --reload --port 8000`

Frontend: `cd frontend`, `npm install`, `npm run dev`

Si sigue mostrándose una carta antigua, reiniciar ambos servidores y recargar el navegador con Ctrl+Shift+R.
