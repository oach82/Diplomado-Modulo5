# Caso de la suite "Carrito" de Azure Test Plans (Dia 3).
# Palabras clave en ingles (Gherkin), texto de los pasos en espanol.
Feature: Agregar productos al carrito
  Como cliente de la tienda
  quiero agregar productos al carrito
  para comprarlos despues

  # @TC19 = ID del Test Case en Azure Test Plans (enlaza el resultado al caso).
  @carrito @smoke @TC19
  Scenario: Agregar un producto al carrito
    Given que abro la home de la tienda
    When agrego el producto 1 al carrito
    Then el contador del carrito muestra 1

  @carrito
  Scenario: Agregar dos productos distintos al carrito
    Given que abro la home de la tienda
    When agrego el producto 1 al carrito
    And agrego el producto 2 al carrito
    Then el contador del carrito muestra 2
