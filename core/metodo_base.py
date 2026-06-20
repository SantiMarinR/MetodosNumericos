from abc import ABC, abstractmethod
from core.resultado import ResultadoMetodo


class MetodoNumerico(ABC):
    nombre = "Método numérico"
    categoria = "General"
    descripcion = "Descripción del método."
    parametros = []

    @abstractmethod
    def ejecutar(self, **kwargs) -> ResultadoMetodo:
        pass
