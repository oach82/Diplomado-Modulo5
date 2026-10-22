# Evidencia de self-healing (verificada end-to-end con Podman)

`healing-select-categoria.png` es el **screenshot real** que generó el backend de
Healenium durante una sanación verificada. Muestra la página de la Tienda con el
`<select>` de categoría **recuadrado en rojo**: ese es el elemento que Healenium
re-encontró después de que el `data-testid` cambió en el HTML de la app.

## Cómo se reprodujo (resumen)

1. `podman compose up -d` → 7 servicios arriba (grid `ready:true`, app `estado:ok`).
2. Corrida sana: `podman compose run --rm tests gradle --no-daemon -DbaseUrl=http://app-tienda:3000 e2e`
   → `3 tests completed, 0 failed`. Healenium aprende 7 selectores
   (`SELECT count(*) FROM healenium.selector` = 7). `healing_result` = 0 filas.
3. Se rompe el HTML de la app: en `app-tienda/public/index.html`,
   `data-testid="filtro-categoria"` → `data-testid="selector-categoria"`
   (el `id` del `<select>` se deja igual).
4. Se aplica el cambio a la app en ejecución y se corre de nuevo **forzando
   re-ejecución** (clave):
   `podman compose run --rm tests gradle --no-daemon --rerun-tasks -DbaseUrl=http://app-tienda:3000 e2e`
5. Resultado verificado:
   - `3 tests completed, 0 failed` + `4 actionable tasks: 4 executed`.
   - `healing_result` → `select#filtro-categoria`, score `0.9642857…` (96.4%), `success_healing = t`.
   - Screenshot generado por el backend en `screenshots/<hash>/screenshot_*.png` (~100 KB).

## Detalle crítico: `--rerun-tasks`

Sin `--rerun-tasks`, Gradle ve los mismos inputs de la corrida sana, marca la tarea
`e2e` como `UP-TO-DATE` y **no vuelve a abrir el navegador**. El test aparece
"verde" pero no hubo intento de búsqueda → no hay healing → `healing_result`
queda en 0 filas. Comprobado durante la verificación.

## Dónde vive la evidencia (versión open-source)

| Evidencia | Dónde |
|-----------|-------|
| Registro de la sanación | tabla `healenium.healing_result` en PostgreSQL |
| Captura visual | volumen `./screenshots:/screenshots` del backend → PNG con el elemento recuadrado |
| Resultado del test | reporte Serenity en `target/site/serenity/` (escenario en verde) |

El dashboard web de Healenium (puerto 5173) es **Healenium Pro** (de pago). Con la
versión open-source, la evidencia son estas tres fuentes.
