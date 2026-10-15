"""
DEMO CONCEPTUAL — Self-healing de selectores en Playwright (Opcion B).

OJO: esto NO es Healenium. Healenium es para Selenium (ver README.md de esta
carpeta). Aqui mostramos el MISMO CONCEPTO implementado a mano en Playwright:
una funcion que intenta el selector oficial y, si falla, prueba selectores
alternativos y AVISA que uso un fallback (para que un humano lo revise).

Idea clave (y la del Bloque 11 de riesgos): el self-healing NUNCA debe tapar
el cambio en silencio. Siempre AVISA. Sanar sin reportar = falsos verdes.

Como probarlo (ilustrativo):
    pip install playwright
    python -m playwright install chromium
    # con la app Tienda corriendo en http://localhost:3000
    python self_healing.py
"""
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout


def localizar_con_fallback(page, candidatos, descripcion, timeout_ms=3000):
    """Intenta cada selector en orden. Usa el primero que exista.

    - Si funciona el PRINCIPAL (indice 0): todo normal, sin aviso.
    - Si funciona un FALLBACK (indice > 0): devuelve el locator PERO avisa
      claramente que el selector oficial fallo y hay que revisar.
    - Si NINGUNO existe: lanza error (no hay nada que sanar).

    candidatos: lista de selectores, del mas confiable (oficial) al mas generico.
    """
    for i, selector in enumerate(candidatos):
        try:
            page.wait_for_selector(selector, timeout=timeout_ms, state="visible")
            if i == 0:
                print(f"[ok] '{descripcion}': selector oficial funciono ({selector})")
            else:
                print(
                    f"[SELF-HEALING] '{descripcion}': el selector oficial "
                    f"'{candidatos[0]}' FALLO. Use el fallback '{selector}'. "
                    f">>> REVISAR: ¿cambio el data-testid (fix) o se rompio el "
                    f"elemento (bug)?"
                )
            return page.locator(selector)
        except PwTimeout:
            continue
    raise AssertionError(
        f"Ningun selector encontro '{descripcion}'. Probados: {candidatos}"
    )


def demo():
    base_url = "http://localhost:3000"
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        page = navegador.new_page()
        page.goto(base_url)

        # El grid de productos. Primero el data-testid OFICIAL; si cambio (como
        # en el ejercicio del dia, grid-productos -> grid-de-productos), caen los
        # fallbacks por clase/estructura y se AVISA.
        grid = localizar_con_fallback(
            page,
            candidatos=[
                '[data-testid="grid-productos"] .card',  # oficial
                '.grid .card',                            # fallback por clase
                'main .card',                             # fallback por estructura
            ],
            descripcion="grid de productos",
        )
        n = grid.count()
        print(f"Resultado: el grid tiene {n} tarjetas visibles.")

        navegador.close()


if __name__ == "__main__":
    demo()
