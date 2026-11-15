# Subasta FC — Reglas V3, iteración de motor

## Partida
- Sala: de 2 a 5 managers. Solo anfitrión inicia, con todos listos.
- Presupuesto inicial configurable: 100–5000 millones. Se reinicia al crear nueva partida.
- Rondas principales configurables: 12–40. Duración por ronda: 15–180 segundos.
- El servidor elige cartas únicas de un catálogo de 185 cartas de prueba.

## Puja
- Precio anunciado inicial: **0 M**. La primera oferta válida es de **1 M**.
- Se permiten importes enteros arbitrarios en millones; no se obliga a múltiplos de 5.
- Cada nueva puja debe superar la mayor oferta por al menos 1 M y no exceder el presupuesto propio.
- La oferta se acepta según el orden de procesamiento del servidor; no se acepta al vencimiento.
- Si llega una oferta válida en los últimos cinco segundos, quedan al menos cinco segundos.
- Un líder no puede superarse a sí mismo. Una carta no se adjudica dos veces.
- La oferta ganadora se descuenta al terminar la ronda; sin ofertas, la carta queda sin comprador.

## Identidad
- Antes de adjudicar, se expone solo el identificador y la silueta (si existe). No se revela el nombre, media ni premios en el estado de subasta.
- Tras cerrar, se revela ficha completa, temporada, edición y comprador.

## Plantilla y resultado
- Formación objetivo 4-3-3: 1 POR, 4 DEF, 3 MED, 3 DEL.
- El ganador es quien tenga la mayor **suma de medias de los 11 titulares válidos**.
- Desempate: presupuesto restante y, luego, identificador de manager.
- La fase de completar XI está implementada **provisionalmente como asignación automática gratuita** de cartas de reserva tras las rondas. El objetivo V3.1 es sustituirla por una selección interactiva, sin dejar equipos incompletos.
- Máximo 14 compras en subasta principal; las cartas fuera de los cupos de posición se guardan como reservas.

## No cubierto aún
- Transferencias entre usuarios, venta directa, subasta secundaria, intercambio mixto, regalos y consentimiento de contraparte.
- Persistencia y seguridad de producción.
