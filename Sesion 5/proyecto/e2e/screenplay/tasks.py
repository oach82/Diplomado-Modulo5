"""Tasks: acciones de negocio de alto nivel.

Cada Task se compone de interactions. Se leen como lo que hace un usuario:
    actor.intenta(AbrirElCatalogo())
    actor.intenta(FiltrarPorCategoria.llamada("hogar"))
    actor.intenta(AgregarProductoAlCarrito.con_id(1))
    actor.intenta(ConfirmarPedido.con_correo("ana@test.com"))
"""
from .interactions import Abrir, HacerClic, Escribir, Seleccionar
from .abilities import NavegarConElNavegador


class AbrirElCatalogo:
    def ejecutar_como(self, actor):
        actor.intenta(Abrir.la_pagina("/"))
        # Esperar a que el grid tenga al menos un producto
        page = actor.habilidad(NavegarConElNavegador).page
        page.wait_for_selector('[data-testid="grid-productos"] .card', timeout=10000)


class FiltrarPorCategoria:
    def __init__(self, categoria: str):
        self.categoria = categoria

    @staticmethod
    def llamada(categoria: str) -> "FiltrarPorCategoria":
        return FiltrarPorCategoria(categoria)

    def ejecutar_como(self, actor):
        actor.intenta(Seleccionar.el_valor(self.categoria).en("filtro-categoria"))


class AgregarProductoAlCarrito:
    def __init__(self, producto_id: int):
        self.producto_id = producto_id

    @staticmethod
    def con_id(producto_id: int) -> "AgregarProductoAlCarrito":
        return AgregarProductoAlCarrito(producto_id)

    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en(f"agregar-{self.producto_id}"))


class AbrirElCarrito:
    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en("abrir-carrito"))
        # Esperar a que el formulario del carrito este listo
        page = actor.habilidad(NavegarConElNavegador).page
        page.wait_for_selector('[data-testid="confirmar-pedido"]', timeout=10000)


class ConfirmarPedido:
    def __init__(self, correo: str):
        self.correo = correo

    @staticmethod
    def con_correo(correo: str) -> "ConfirmarPedido":
        return ConfirmarPedido(correo)

    def ejecutar_como(self, actor):
        actor.intenta(
            Escribir.el_texto(self.correo).en("input-email"),
            HacerClic.en("confirmar-pedido"),
        )
        # El pedido se crea via fetch (async) y luego cambia la vista:
        # esperar a que aparezca la confirmacion antes de seguir.
        page = actor.habilidad(NavegarConElNavegador).page
        page.wait_for_selector('[data-testid="vista-exito"].activa', timeout=10000)
