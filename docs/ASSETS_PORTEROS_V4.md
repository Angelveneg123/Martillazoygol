# Integración de porteros — Subasta FC V4

Se integraron los archivos de `porteros.zip` como assets estáticos de Vite en `frontend/public/goalkeepers/`. El catálogo autoritativo se encuentra en `backend/players.json`.

- Las imágenes `*_SILUETA.png` aparecen mientras la subasta está activa. El servidor no entrega nombre, media ni edición de la carta actual hasta la revelación.
- Al terminar, la interfaz usa la imagen `*_CARTA_*.png` y presenta nombre, edición, año, media y nacionalidad.
- La alineación muestra las cartas de los porteros adquiridos.
- Se incluyen hasta cinco porteros con assets por partida para que tengan presencia en la subasta. Los demás quedan disponibles para completar el XI.
- Las medias proceden del catálogo suministrado y son valores de videojuego, no calificaciones oficiales. Los premios y clubes no venían en el catálogo: se dejan vacíos/no especificados, sin inventarlos.
- Las imágenes son de prototipo y no se ha verificado su licencia comercial.

## Pendiente

Recibir assets de defensas, medios y delanteros; sustituir las cartas provisionales restantes y crear un catálogo uniforme. El sistema de regalos, traspasos y pujas entre managers no está implementado en esta versión.
