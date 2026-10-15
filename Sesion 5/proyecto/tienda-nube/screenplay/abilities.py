"""Abilities: lo que un actor PUEDE hacer."""
from playwright.sync_api import Page


class NavegarConElNavegador:
    """Habilidad de usar un navegador (una Page de Playwright).

    Guarda tambien la URL base de la app para construir rutas.
    """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def usando(page: Page, base_url: str) -> "NavegarConElNavegador":
        return NavegarConElNavegador(page, base_url)
