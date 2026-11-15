# Subasta FC V9 — Gestión de salas y configuración

Base: V8 Defensas Completas (24 defensas).

- Salir de la sala con confirmación desde lobby, subasta y resultados.
- El servidor elimina al participante de la sala; si era anfitrión, transfiere el rol.
- Si queda vacía, elimina la sala. Una desconexión de red no equivale a abandonar.
- Configuración de presupuesto: enteros de 1 a 5000 millones. El valor 0 no permite pujar y queda rechazado en frontend y backend.
- Rondas: 12 a 40. Duración: 30 a 180 segundos en la interfaz.
- Campos numéricos sin controles de flechas y con validación antes de crear sala.

**Nota:** la partida multijugador completa y el APK deben verificarse en el entorno del usuario.
