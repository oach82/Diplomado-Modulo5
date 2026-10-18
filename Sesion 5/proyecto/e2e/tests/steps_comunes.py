"""Steps compartidos entre features (Given/When/Then reutilizables)."""
from pytest_bdd import given, when, then, parsers

from screenplay.tasks import (
    AbrirElCatalogo,
    FiltrarPorCategoria,
    AgregarProductoAlCarrito,
    AbrirElCarrito,
    ConfirmarPedido,
)
from screenplay.questions import (
    ContadorCarrito,
    ProductosVisibles,
    CategoriasVisibles,
    NumeroDePedido,
    MensajeDeExitoVisible,
)


# ── GIVEN / DADO ──────────────────────────────────────────────────
@given("que abro la home de la tienda")
def abrir_home(actor):
    actor.intenta(AbrirElCatalogo())


# ── WHEN / CUANDO ─────────────────────────────────────────────────
@when(parsers.parse('filtro el catalogo por la categoria "{categoria}"'))
def filtrar_categoria(actor, categoria):
    actor.intenta(FiltrarPorCategoria.llamada(categoria))


@when(parsers.parse("agrego el producto {producto_id:d} al carrito"))
@given(parsers.parse("agrego el producto {producto_id:d} al carrito"))
def agregar_producto(actor, producto_id):
    actor.intenta(AgregarProductoAlCarrito.con_id(producto_id))


@when(parsers.parse('abro el carrito y confirmo el pedido con el correo "{correo}"'))
def abrir_y_confirmar(actor, correo):
    actor.intenta(AbrirElCarrito(), ConfirmarPedido.con_correo(correo))


# ── THEN / ENTONCES ───────────────────────────────────────────────
@then(parsers.parse('solo veo productos de la categoria "{categoria}"'))
def solo_categoria(actor, categoria):
    categorias = actor.pregunta(CategoriasVisibles.lista())
    assert all(c == categoria for c in categorias), (
        f"Se esperaban solo '{categoria}', pero hay: {set(categorias)}"
    )


@then("la cantidad de productos visibles es mayor que cero")
def hay_productos(actor):
    assert actor.pregunta(ProductosVisibles.cantidad()) > 0


@then(parsers.parse("el contador del carrito muestra {esperado:d}"))
def contador_carrito(actor, esperado):
    assert actor.pregunta(ContadorCarrito.valor()) == esperado


@then("veo el mensaje de pedido confirmado")
def mensaje_confirmado(actor):
    assert actor.pregunta(MensajeDeExitoVisible.estado()) is True


@then("el numero de pedido no esta vacio")
def numero_pedido(actor):
    assert actor.pregunta(NumeroDePedido.texto()) != ""
