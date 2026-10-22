# language: es
@e2e @carrito
Característica: Carrito de compras
  Como cliente de la Tienda
  quiero agregar productos al carrito
  para comprarlos después

  Antecedentes:
    Dado que Ana abre la home de la tienda

  @TC19
  Escenario: Agregar un producto al carrito
    Cuando Ana agrega el producto 1 al carrito
    Entonces el contador del carrito muestra 1

  @TC21
  Escenario: Agregar dos productos distintos al carrito
    Cuando Ana agrega el producto 1 al carrito
    Y Ana agrega el producto 2 al carrito
    Entonces el contador del carrito muestra 2
