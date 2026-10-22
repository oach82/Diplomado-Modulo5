"""
CONSUMER — Servicio de Notificaciones (Dia 6, contract testing con Pact).

Este es un servicio NUEVO y pequeno que CONSUME la API de la Tienda (el provider).
Imagina que su trabajo real es: cuando hay que notificar algo de un producto
(ej. "bajo stock"), consulta el producto a la API de la Tienda y arma el mensaje.

Lo unico que nos importa para Pact: este servicio hace una peticion HTTP al
provider (GET /api/productos/:id) y espera una respuesta con cierta FORMA
(id, nombre, precio...). Esa expectativa es el CONTRATO.

El cliente NO sabe (ni le importa) como esta hecho el provider por dentro; solo
depende de la forma de la respuesta. Por eso Pact valida la FORMA, no los datos
exactos.
"""
import requests


class ClienteProductos:
    """Cliente HTTP minimo contra la API de la Tienda (el provider)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def obtener_producto(self, producto_id: int) -> dict:
        """GET /api/productos/:id -> dict del producto. Lanza si no es 200."""
        r = requests.get(f"{self.base_url}/api/productos/{producto_id}", timeout=5)
        r.raise_for_status()
        return r.json()

    def resumen_para_notificar(self, producto_id: int) -> str:
        """Logica de negocio del consumer: arma un mensaje con el producto.

        Depende de que la respuesta tenga 'nombre' y 'precio'. Eso es,
        justamente, lo que el contrato Pact va a asegurar.
        """
        p = self.obtener_producto(producto_id)
        return f"Producto '{p['nombre']}' (${p['precio']:.2f}) disponible."
