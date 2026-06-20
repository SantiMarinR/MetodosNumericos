from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResultadoMetodo:
    resultado: Any = None
    mensaje: str = ""
    pasos: list = field(default_factory=list)
    tabla: list = field(default_factory=list)
