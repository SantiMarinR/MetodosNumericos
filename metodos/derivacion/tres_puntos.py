from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class TresPuntos(MetodoNumerico):
    nombre = "Derivación por 3 puntos"
    categoria = "Derivación"
    descripcion = "Aquí va la explicación breve del método."

    parametros = [
        # Ejemplo:
        # {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**3 - x - 2"},
        # {"nombre": "a", "label": "Valor de a", "tipo": "number", "placeholder": "1"},
        # {"nombre": "b", "label": "Valor de b", "tipo": "number", "placeholder": "2"},
    ]

    def ejecutar(self, **kwargs):
        return ResultadoMetodo(
            resultado=None,
            mensaje="Este método todavía no ha sido programado.",
            pasos=[
                "Abre el archivo de este método.",
                "Define los parámetros que necesita.",
                "Programa el método dentro de ejecutar()."
            ],
            tabla=[]
        )
