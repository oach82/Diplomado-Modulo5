# Demo conceptual — Self-healing de selectores (Parte C del Día 5)

Esta carpeta es **material de demostración** para la Parte C del Día 5. No es
parte del pipeline ni del framework principal: es ilustrativa.

## Qué es self-healing

Cuando un selector (ej. un `data-testid`) deja de encontrar su elemento porque
el DOM cambió, el *self-healing* busca automáticamente el elemento **más
parecido**, deja que la prueba continúe y **reporta** que "sanó". Así una suite
no se cae entera por un cambio menor de UI.

## Healenium (la herramienta de mercado) — ¿por qué NO está aquí?

**Healenium** (https://healenium.io) es la herramienta open source más conocida
de self-healing. Importante y honesto:

- **Healenium es para Selenium** (Java y Python con Selenium WebDriver).
- Nuestro framework es **Playwright + pytest-bdd**.
- Por eso **Healenium NO se integra directamente** a nuestro proyecto.

Cómo funciona Healenium (para conocerlo):

1. Guarda una "huella" de cada elemento la primera vez (en PostgreSQL).
2. Cuando un localizador falla, compara el DOM actual contra esa huella y elige
   el nodo **más similar** (algoritmo de similitud de árbol).
3. Usa ese nodo para continuar y **registra** el healing en un reporte.
4. Un humano revisa el reporte: ¿fue un fix legítimo o tapó un bug?

Necesita un stack aparte: **Selenium WebDriver + servicio Healenium + base de
datos (PostgreSQL)**, normalmente con Docker. Es otro ecosistema, por eso en el
curso lo vemos como **concepto**, no lo montamos.

## Lo que SÍ corre aquí: self-healing casero en Playwright (Opción B)

`self_healing.py` implementa el **mismo concepto** a mano en Playwright: una
función `localizar_con_fallback()` que intenta el selector oficial y, si falla,
prueba selectores alternativos (por clase, por estructura) y **avisa** que usó
un fallback.

```powershell
pip install playwright
python -m playwright install chromium
# con la app Tienda del Día 5 corriendo en http://localhost:3000
python self_healing.py
```

Para ver el "healing" en acción: cambia en la app el `data-testid="grid-productos"`
por `grid-de-productos` (el mismo cambio del ejercicio del día) y corre el script.
Verás el mensaje `[SELF-HEALING] ... REVISAR` porque el oficial falló y usó un
fallback.

## La regla de oro (Bloque 11 — riesgos)

El self-healing, sea Healenium o casero, **siempre debe AVISAR** que sanó —
nunca tapar el cambio en silencio. Si no, caes en:

- **Falsos verdes**: la prueba pasa pero ya no valida lo que debía.
- **Enmascarar bugs**: "arregla" el selector y oculta que el elemento real se rompió.

Por eso: **self-healing con supervisión humana** (sana y reporta) `>`
**self-healing automático** (sana y nadie revisa). La IA y el self-healing
aceleran; la decisión de qué entra al código es siempre de una persona.
