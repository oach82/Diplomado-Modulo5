"""Interactions: acciones atomicas de bajo nivel sobre la Page.

Son los ladrillos con los que se construyen las Tasks. Cada una sabe
ejecutarse "como" un actor usando su habilidad de navegar.
"""
from .abilities import NavegarConElNavegador


def _page(actor):
    return actor.habilidad(NavegarConElNavegador).page


def _base(actor):
    return actor.habilidad(NavegarConElNavegador).base_url


class Abrir:
    """Abre una ruta relativa a la base_url (ej. '/')"""

    def __init__(self, ruta: str):
        self.ruta = ruta

    @staticmethod
    def la_pagina(ruta: str = "/") -> "Abrir":
        return Abrir(ruta)

    def ejecutar_como(self, actor):
        _page(actor).goto(_base(actor) + self.ruta)


class HacerClic:
    """Clic sobre un elemento por data-testid."""

    def __init__(self, testid: str):
        self.testid = testid

    @staticmethod
    def en(testid: str) -> "HacerClic":
        return HacerClic(testid)

    def ejecutar_como(self, actor):
        _page(actor).get_by_test_id(self.testid).click()


class Escribir:
    """Escribe texto en un input por data-testid."""

    def __init__(self, texto: str, testid: str):
        self.texto = texto
        self.testid = testid

    @staticmethod
    def el_texto(texto: str) -> "Escribir":
        e = Escribir(texto, "")
        return e

    def en(self, testid: str) -> "Escribir":
        self.testid = testid
        return self

    def ejecutar_como(self, actor):
        _page(actor).get_by_test_id(self.testid).fill(self.texto)


class Seleccionar:
    """Selecciona un valor en un <select> por data-testid."""

    def __init__(self, valor: str, testid: str):
        self.valor = valor
        self.testid = testid

    @staticmethod
    def el_valor(valor: str) -> "Seleccionar":
        return Seleccionar(valor, "")

    def en(self, testid: str) -> "Seleccionar":
        self.testid = testid
        return self

    def ejecutar_como(self, actor):
        _page(actor).get_by_test_id(self.testid).select_option(self.valor)
