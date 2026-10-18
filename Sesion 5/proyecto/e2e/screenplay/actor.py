"""Actor: el protagonista de la prueba.

Un actor tiene habilidades (abilities), ejecuta tareas (intenta/attempts_to)
y responde preguntas (pregunta/asks) sobre el estado de la aplicacion.
"""
from typing import Any


class Actor:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self._habilidades: dict[type, Any] = {}

    # ── Habilidades ──────────────────────────────────────────────
    @staticmethod
    def llamado(nombre: str) -> "Actor":
        return Actor(nombre)

    def que_puede(self, *habilidades) -> "Actor":
        """Dota al actor de una o varias habilidades."""
        for h in habilidades:
            self._habilidades[type(h)] = h
        return self

    def habilidad(self, tipo: type):
        """Recupera una habilidad por su tipo. Falla claro si no la tiene."""
        if tipo not in self._habilidades:
            raise AssertionError(
                f"{self.nombre} no tiene la habilidad {tipo.__name__}"
            )
        return self._habilidades[tipo]

    # ── Tareas y preguntas ───────────────────────────────────────
    def intenta(self, *tareas) -> "Actor":
        """Ejecuta tareas/interacciones en orden (performs_as)."""
        for t in tareas:
            t.ejecutar_como(self)
        return self

    def pregunta(self, pregunta) -> Any:
        """Resuelve una pregunta (answered_by) y devuelve su valor."""
        return pregunta.responder_como(self)
