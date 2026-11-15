# Subasta FC V10 — Mercado y gestión de plantilla

Base: Subasta FC V9 (ZIP entregado por el usuario).

## Funciones nuevas
- Selección de cartas propias en el campo y en reservas.
- Asignación de titular compatible con su posición; el ocupante anterior pasa a reserva.
- Regalos de cartas a otro manager (requieren aceptación).
- Ventas a precio fijo entre managers (requieren aceptación).
- Intercambios de cartas con dinero opcional en cualquiera de las direcciones.
- Propuestas pendientes, aceptación, rechazo y cancelación.
- Validación autoritativa en FastAPI y difusión de estado vía WebSocket.
- Actualización del once y de resultados al completar operaciones.

## Alcance y pendientes
- El mercado funciona dentro de la misma sala y partida; no hay comercio entre salas.
- Los intercambios no son subastas abiertas: esa modalidad queda para una entrega posterior.
- El sistema sigue utilizando almacenamiento en memoria; al reiniciar FastAPI se pierden las salas.
- La compilación web y las pruebas reales de dos navegadores requieren verificación local.
- No se ha generado un APK; el proyecto conserva la configuración Capacitor.

## Prueba sugerida
1. Abrir dos navegadores y entrar en la misma sala.
2. Conseguir dos cartas para un mismo puesto (p.ej. Cafú y Dalot).
3. Abrir **Mi once y mercado**, seleccionar Cafú y pulsar **Poner en LD**.
4. Elegir **Regalar**, **Vender** o **Intercambiar** y enviar propuesta al segundo manager.
5. En el otro navegador, aceptar o rechazar.
6. Confirmar que las cartas y presupuestos se actualizan en ambos navegadores.
