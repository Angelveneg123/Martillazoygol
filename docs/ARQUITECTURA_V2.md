# SUBASTA FC — Arquitectura técnica V2 (etapa 1)

**Estado:** arquitectura objetivo aprobable; implementación existente conservada como referencia funcional, no como diseño definitivo.  
**Plataforma:** React + TypeScript + Vite + Capacitor (Android), Python + FastAPI + WebSockets.  
**Capacidad:** 2–5 managers por sala privada.

## 1. Decisión de producto

La V2 se desarrolla **por etapas** y no se aceptará una pantalla bonita que no respete las reglas de servidor. El alcance del primer hito es **crear/unirse a una sala y lobby**. Subasta, equipo y resultados se integran después, cada uno con pruebas.

## 2. Estructura objetivo (monorepo)

```text
subasta-fc/
├── apps/
│   └── mobile/                     # React + Vite + Capacitor
│       ├── src/
│       │   ├── app/                 # Router, providers, bootstrap
│       │   ├── pages/               # Home, Room, Lobby, Auction, Squad, Results
│       │   ├── features/
│       │   │   ├── rooms/           # Crear/unirse, código, estado de sala
│       │   │   ├── auction/         # Temporizador, pujas, historial
│       │   │   ├── squad/           # Plantilla, formación, puntuación
│       │   │   └── profile/         # Posterior al MVP
│       │   ├── components/ui/       # Button, Card, Modal, Toast, Header
│       │   ├── services/            # WebSocket, REST, persistencia local
│       │   ├── stores/              # Estado local; servidor es autoridad
│       │   ├── styles/              # Tokens, tipografía, breakpoints
│       │   └── assets/              # Cartas ficticias e iconos
│       ├── capacitor.config.ts
│       └── package.json
├── services/
│   └── game-api/
│       ├── app/
│       │   ├── main.py             # Composición FastAPI
│       │   ├── api/                # Health y endpoints REST
│       │   ├── ws/                 # Gateway de eventos
│       │   ├── domain/             # Reglas puras, entidades, puntuación
│       │   ├── application/        # Casos de uso: sala, puja, ronda
│       │   ├── infrastructure/     # Repositorios y pub/sub
│       │   └── schemas/            # Validación de mensajes
│       └── tests/                  # Unitarias, integración, concurrencia
├── packages/
│   └── contracts/                  # Esquemas JSON versionados
├── content/
│   └── players.json               # Catálogo ficticio beta
├── docs/
│   ├── ARQUITECTURA_V2.md
│   ├── REGLAS_V2.md
│   └── PLAN_DE_ENTREGAS.md
└── README.md
```

**Nota:** el ZIP incluye el prototipo anterior en `frontend/` y `backend/`, con el cupo corregido. El árbol anterior es la **estructura objetivo**, no carpetas ya implementadas. La migración será incremental para no romper las pruebas existentes.

## 3. Límites y responsabilidades

| Capa | Responsabilidad | Nunca debe hacer |
|---|---|---|
| React | Mostrar estado, capturar acciones, feedback accesible | Decidir ganador o saldo |
| WebSocket gateway | Autenticar sesión, validar esquema, distribuir eventos | Calcular resultados por su cuenta |
| Application | Orquestar crear/unirse, iniciar, pujar, cerrar ronda | Acceder directamente a componentes UI |
| Domain | Reglas de elegibilidad, incrementos, adjudicación, ranking | Depender de FastAPI o Firebase |
| Infrastructure | Guardar estado, locks, persistencia, Redis futuro | Definir reglas de negocio |

## 4. Protocolo versionado propuesto

Mensajes cliente: `room.create`, `room.join`, `room.ready`, `room.start`, `auction.bid`, `room.resume`. Cada comando incluye `requestId` único para idempotencia. Eventos servidor: `room.snapshot`, `auction.bid_accepted`, `auction.bid_rejected`, `auction.round_closed`, `game.finished`. El servidor adjunta `serverTime`, `roomVersion` y `roundId`. **Estos contratos son objetivo V2, no están implementados aún**: el prototipo anterior conserva `create`, `join`, `ready`, `start`, `bid`.

## 5. Modelo de dominio

- `Room`: código, anfitrión, fase, versión, configuración, participantes.
- `Participant`: identificador, nombre, listo, conectado, presupuesto, plantilla.
- `AuctionRound`: índice, carta, base, líder, importe, fin servidor, estado.
- `Bid`: idempotency key, participante, ronda, importe, instante servidor.
- `Card`: id, nombre ficticio, posición, valoración, precio base.
- `Result`: puntuación, ajuste posicional, presupuesto, clasificación.

## 6. Concurrencia y seguridad

1. **El servidor decide**: dos pujas simultáneas se ordenan bajo un bloqueo por sala.
2. Solo el ganador confirmado paga al cierre; el cierre debe ser idempotente.
3. El reloj es del servidor; una puja aceptada en los últimos 5 s extiende la ronda.
4. Reconexión: el cliente solicita snapshot completo y descarta eventos con versiones antiguas.
5. En la beta local hay estado en memoria y un solo proceso; para despliegue real se requiere almacenamiento persistente, autenticación segura, rate limiting y coordinación multiinstancia.
6. Android se conecta a un servidor **HTTPS/WSS público**; `localhost` del teléfono no es el ordenador.

## 7. Diseño UI/UX V2

- **Identidad:** azul-negro `#07111F`, superficie `#102238`, verde `#36E59B`, dorado `#EFC46A`, texto `#F4F8FC`.
- **Tipografía:** jerarquía compacta; títulos claros, métricas grandes, textos secundarios legibles.
- **Mobile-first:** 320–430 px, áreas táctiles ≥44 px, respetar safe areas de Android.
- **Inicio:** una acción primaria «Crear sala» y secundaria «Unirse con código»; no saturar con 16 accesos.
- **Lobby:** código copiable, cupo `n/5`, host visible, estados listo/conectado y botón iniciar condicionado.
- **Subasta:** cronómetro, carta, puja, saldo y fichajes siempre visibles; confirmación de aceptación/rechazo.
- **Estados obligatorios:** cargando, sin conexión, reconectando, error, sala llena, sala iniciada.
- **No depender del color** para mostrar aceptación, líder o errores.

## 8. Decisiones que evitan errores de diseño

- Con 5 participantes, 24 cartas **no alcanzan para 11 fichajes por persona**. La plantilla de 11 es un objetivo y el resultado admite equipos incompletos. Antes de cerrar el modo «XI completo» se debe diseñar una reserva de cartas y duración de partida diferente.
- Separamos **moneda de partida** de monedas de progresión; no se monetiza la beta.
- Las 16 pantallas siguen siendo la visión completa; el MVP solo implementa el ciclo competitivo.
- No se promete APK listo hasta verificar `npm run build`, `npx cap sync android` y una compilación Gradle real.

## 9. Criterio de salida de la etapa 1

- [ ] React con estructura modular, rutas y componentes reutilizables.
- [ ] Home y Lobby rediseñados y adaptados a Android.
- [ ] 2–5 participantes pueden crear/unirse a una sala desde dispositivos distintos.
- [ ] Host, cupos, listo y desconexión sincronizados.
- [ ] Pruebas de servidor para sexto usuario rechazado y reconexión.
- [ ] Build web y sincronización Capacitor verificados.
