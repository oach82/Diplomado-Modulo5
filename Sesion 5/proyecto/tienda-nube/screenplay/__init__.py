"""Patron Screenplay sobre Playwright (Python).

Capas:
  - actor      : quien hace las cosas (el usuario de la prueba)
  - abilities  : lo que el actor PUEDE hacer (ej. navegar con un navegador)
  - tasks      : acciones de negocio de alto nivel (ej. "Agregar al carrito")
  - interactions: acciones atomicas de bajo nivel (click, escribir, abrir)
  - questions  : lo que el actor OBSERVA para verificar (ej. "contador del carrito")

La gracia del patron: los tests se leen como lenguaje de negocio
    actor.intenta(AgregarAlCarrito.el_producto(1))
    assert actor.pregunta(ContadorCarrito.valor()) == 1
"""
