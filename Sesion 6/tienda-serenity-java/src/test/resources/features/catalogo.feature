# language: es
@e2e @catalogo
Característica: Catálogo de productos
  Como cliente de la Tienda
  quiero ver y filtrar el catálogo
  para encontrar productos de una categoría

  Antecedentes:
    Dado que Ana abre la home de la tienda

  @TC20 @healenium
  Escenario: Filtrar el catálogo por la categoría hogar
    Cuando Ana filtra el catálogo por la categoría "hogar"
    Entonces Ana solo ve productos de la categoría "hogar"
    Y la cantidad de productos visibles es mayor que cero
