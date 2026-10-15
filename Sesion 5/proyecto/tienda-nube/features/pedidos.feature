# Caso de la suite "Pedidos" de Azure Test Plans (Dia 3).
# Palabras clave en ingles (Gherkin), texto de los pasos en espanol.
Feature: Confirmar un pedido
  Como cliente de la tienda
  quiero confirmar un pedido con un producto en el carrito
  para completar mi compra

  # @TC21 = ID del Test Case en Azure Test Plans (enlaza el resultado al caso).
  @pedidos @smoke @TC21
  Scenario: Confirmar un pedido con un producto
    Given que abro la home de la tienda
    And agrego el producto 1 al carrito
    When abro el carrito y confirmo el pedido con el correo "ana@tienda-qa.com"
    Then veo el mensaje de pedido confirmado
    And el numero de pedido no esta vacio
