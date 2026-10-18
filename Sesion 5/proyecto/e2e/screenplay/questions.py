"""Questions: lo que el actor OBSERVA para verificar un resultado.

Cada Question sabe responderse "como" un actor y devuelve un valor
que el test compara con un assert.
"""
from .abilities import NavegarConElNavegador


def _page(actor):
    return actor.habilidad(NavegarConElNavegador).page


class ContadorCarrito:
    """Numero que muestra el contador del carrito en el header."""

    @staticmethod
    def valor() -> "ContadorCarrito":
        return ContadorCarrito()

    def responder_como(self, actor) -> int:
        texto = _page(actor).get_by_test_id("contador-carrito").inner_text()
        return int(texto.strip())


class ProductosVisibles:
    """Cantidad de tarjetas de producto visibles en el catalogo."""

    @staticmethod
    def cantidad() -> "ProductosVisibles":
        return ProductosVisibles()

    def responder_como(self, actor) -> int:
        return _page(actor).locator('[data-testid="grid-productos"] .card').count()


class CategoriasVisibles:
    """Lista de categorias (data-categoria) de las tarjetas visibles."""

    @staticmethod
    def lista() -> "CategoriasVisibles":
        return CategoriasVisibles()

    def responder_como(self, actor) -> list[str]:
        tarjetas = _page(actor).locator('[data-testid="grid-productos"] .card')
        n = tarjetas.count()
        return [tarjetas.nth(i).get_attribute("data-categoria") for i in range(n)]


class TotalDelCarrito:
    """Texto del total mostrado en el carrito (ej. 'Total: $123.00')."""

    @staticmethod
    def texto() -> "TotalDelCarrito":
        return TotalDelCarrito()

    def responder_como(self, actor) -> str:
        return _page(actor).get_by_test_id("carrito-total").inner_text()


class NumeroDePedido:
    """Numero de pedido mostrado en la pantalla de confirmacion."""

    @staticmethod
    def texto() -> "NumeroDePedido":
        return NumeroDePedido()

    def responder_como(self, actor) -> str:
        return _page(actor).get_by_test_id("numero-pedido").inner_text().strip()


class MensajeDeExitoVisible:
    """True si la pantalla de confirmacion de pedido es visible."""

    @staticmethod
    def estado() -> "MensajeDeExitoVisible":
        return MensajeDeExitoVisible()

    def responder_como(self, actor) -> bool:
        return _page(actor).get_by_test_id("mensaje-exito").is_visible()
