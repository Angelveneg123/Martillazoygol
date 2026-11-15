# SUBASTA FC — Requisitos funcionales y reglas cerradas

**Versión:** 1.1-beta (actualización de cupo) · **Estado:** especificación implementable del prototipo · **Fecha:** 2026-11-13

## 1. Propósito y trazabilidad

Juego multijugador de estrategia futbolística: crear o unirse a salas, competir en subastas en tiempo real, gestionar un presupuesto, fichar cartas y comparar plantillas. Esta especificación desarrolla el resumen original del proyecto. **Las cifras y fórmulas siguientes son decisiones nuevas de diseño para la beta, no reglas presentes en el resumen original.**

## 2. Plataforma y arquitectura

- Cliente: React 19 + TypeScript + Vite, diseño mobile-first.
- Empaquetado Android: Capacitor 7, identificador `com.subastafc.app`.
- Servidor autoritativo: Python, FastAPI, WebSockets JSON.
- Contenido: 36 cartas ficticias en JSON; baraja de 24 cartas aleatorias sin repetición por partida.
- Persistencia: **no implementada** en la beta; salas en memoria del proceso. Reiniciar el servidor elimina las partidas.
- Firebase Authentication, PostgreSQL, Redis y recursos comerciales: **fase de producción, no implementados**.

## 3. Requisitos funcionales MVP

| ID | Requisito | Criterio de aceptación | Estado |
|---|---|---|---|
| RF-01 | Identificación básica | El manager introduce nombre de 1-22 caracteres; token local generado por servidor | Implementado; no autenticación segura |
| RF-02 | Crear sala | El servidor genera código alfanumérico de 6 caracteres y designa anfitrión | Implementado |
| RF-03 | Unirse a sala | Código válido, lobby abierto y máximo 5 managers | Implementado |
| RF-04 | Lobby | Lista de managers, conexión y estado listo; inicio por anfitrión | Implementado |
| RF-05 | Subasta en vivo | Carta, valoración, precio, líder y vencimiento sincronizados | Implementado |
| RF-06 | Validación de pujas | Incrementos, presupuesto, cupo, tiempo y líder validados en backend | Implementado |
| RF-07 | Adjudicación | Una carta por ronda, un ganador, un único descuento | Implementado en un proceso |
| RF-08 | Plantilla | Mostrar fichajes agrupados por posición y límite de 11 | Implementado; sin edición táctica |
| RF-09 | Resultados | Clasificación por puntuación reproducible | Implementado |
| RF-10 | Reconexión | Recuperar sala mediante código y token guardados en el mismo navegador | Implementado de forma básica |
| RF-11 | Android | Configuración de Capacitor para compilar APK | Preparado; APK no precompilado |
| RF-12 | Chat, mercado, misiones, tienda, ranking global, perfil, minijuego | Ampliaciones previstas en las 16 pantallas | Fuera del MVP |

## 4. Reglas cerradas de partida V1.0

**R-01.** Sala privada de 2 a 5 participantes. Solo el anfitrión inicia, cuando todos han marcado «Listo». No se admiten participantes nuevos después del inicio.

**R-02.** Cada participante inicia con **500M**, moneda exclusiva de esa partida. No existe conversión a monedas de tienda ni compras con dinero real.

**R-03.** Se sortean **24 cartas distintas** del catálogo de 36 cartas ficticias. Se muestra una carta por ronda; el máximo por manager es **11 fichajes**. La partida termina después de 24 rondas o cuando todos completan 11 cartas.

**R-04.** Cada ronda dura inicialmente **20 segundos**, medidos por el reloj del servidor. El cliente muestra una estimación del tiempo restante a partir de la hora enviada por el servidor.

**R-05.** Cada carta tiene un precio base de 10M a 50M. La primera puja debe ser al menos el precio base; cada puja posterior aumenta un mínimo de **5M** y todas las pujas deben ser múltiplos de 5M. No se permiten pujas de valor no entero.

**R-06.** Una puja es inválida si se recibe después del vencimiento, supera el saldo, excede el límite de plantilla, no alcanza el mínimo o proviene del líder actual.

**R-07.** El servidor procesa las pujas de una sala dentro de un bloqueo de exclusión mutua. El orden efectivo es el orden de procesamiento bajo dicho bloqueo, no el reloj del dispositivo.

**R-08.** Si una puja válida se recibe cuando quedan menos de 5 segundos, la fecha de cierre se extiende hasta 5 segundos desde la aceptación. No existe un máximo de extensiones.

**R-09.** Si no hay pujas, la carta queda sin vender. Si hay pujas, se adjudica al último líder válido y el coste se descuenta **una sola vez**, al cerrar la ronda. Las pujas no descuentan saldo anticipadamente.

**R-10.** Las desconexiones no cancelan las pujas previas ni detienen el reloj. Si un participante se reconecta con el mismo token, recupera el estado. El anfitrión desconectado no puede iniciar una partida nueva hasta reconectarse.

**R-11.** Plantilla objetivo 4-3-3: 1 POR, 4 DEF, 3 MED y 3 DEL. En esta beta no hay alineación manual: las cartas se agrupan por posición y el sistema cuenta hasta la capacidad de cada grupo.

**R-12.** Puntuación final: `suma de valoraciones de todas las cartas + 2 × número de posiciones compatibles (máximo 11) + 10 si hay 11 cartas`. La valoración de cada carta es un entero de 72 a 94. El equipo incompleto también recibe puntuación. La fórmula **no simula un partido real** ni incluye química entre clubes o nacionalidades.

**R-13.** Gana la mayor puntuación. Si hay empate, gana quien conserva más presupuesto; si persiste, se utiliza el identificador de jugador en orden ascendente para una clasificación determinista.

**R-14.** El resultado se publica para todos al finalizar. No se otorgan XP, monedas permanentes ni premios en esta beta.

## 5. Mensajes WebSocket

Conexión a `/ws`. El cliente envía objetos JSON con `action`:

- `create`: `{ "action":"create", "name":"Manager" }`
- `join`: `{ "action":"join", "name":"Manager", "code":"ABC123", "token":"TOKEN_OPCIONAL" }`
- `ready`: `{ "action":"ready", "ready":true }`
- `start`: `{ "action":"start" }`
- `bid`: `{ "action":"bid", "amount":50 }`

Servidor responde con `identity`, `state` o `error`. Cada `state` incluye estado público completo y `serverTime` en milisegundos UTC.

## 6. Requisitos no funcionales

- RNF-01: diseño responsivo desde 320 px, botones de al menos 44 px de altura.
- RNF-02: la validación de pujas nunca depende de la interfaz.
- RNF-03: servidor único para esta beta; no ejecutar múltiples workers sin almacenamiento/locks distribuidos.
- RNF-04: para dispositivos Android reales, servidor público con HTTPS/WSS y certificado válido.
- RNF-05: los nombres de futbolistas de prueba son ficticios; no se distribuyen fotografías ni marcas licenciadas.
- RNF-06: para producción, autenticación robusta, persistencia transaccional, rate limiting, validación de origen, pruebas de carga, métricas y seguridad son obligatorios.

## 7. Pruebas de aceptación

1. Dos navegadores independientes crean y se unen a la misma sala.
2. Ambos marcan listo y el anfitrión inicia.
3. Ambos ven la misma carta, puja actual y líder.
4. Una puja de 5M por debajo del mínimo es rechazada.
5. Una puja superior al saldo es rechazada.
6. Una puja aceptada en los últimos 5 segundos extiende la ronda.
7. Al cerrar, solo el ganador recibe la carta y se descuenta una vez.
8. Recargar el navegador conserva la identidad y recupera la sala mientras el servidor permanezca activo.
9. Al terminar las rondas, todos ven la misma clasificación.
10. La compilación web produce `dist/`, y Capacitor sincroniza ese contenido con Android.

## 8. Alcance pendiente para el producto final

Faltan registro real, persistencia, recuperación tras reinicio, múltiples instancias, anti-trampas avanzado, emparejamiento, chat moderado, gestión táctica interactiva, química real, mercado, misiones, tienda, clasificación persistente, audio, accesibilidad auditada, pruebas de rendimiento y compilación APK firmada. El documento cierra las reglas **de esta beta**, no del juego comercial definitivo.
