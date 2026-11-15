# Subasta FC V12 — Subasta persistente

- En Mi XI/Mercado y Chat, panel persistente con precio actual, líder, ronda y tiempo restante.
- Puja rápida desde cualquier pestaña: importe entero en millones, mínimo 1M de incremento, presupuesto validado en cliente y servidor.
- Estado de revelación y botón para ver la carta cuando termina la ronda.
- En móvil, panel fijo encima de la navegación inferior con márgenes para áreas seguras Android/iOS. En escritorio, panel sticky.
- El reloj sigue utilizando `endsAt` del servidor, sincronizado con `serverTime`; la validación definitiva de pujas permanece en FastAPI.
- Se conservan cartas, catálogo, chat, transferencias y las reglas existentes.

## Pruebas manuales
1. Abrir dos navegadores con distintos managers.
2. En uno entrar a Mi XI, en otro pujar: debe actualizarse la barra sin salir de Mi XI.
3. Pujar desde la barra y comprobar actualización en ambos clientes.
4. Comprobar que no se permite pujar por encima del saldo, ni superarse a sí mismo, ni pujar después del cierre.
5. Cambiar a Chat y esperar fin de ronda: la barra debe mostrar la revelación.
6. Probar 320, 360, 390, 430 px y escritorio.
