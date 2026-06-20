from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class SimpsonTresOctavosSimple(MetodoNumerico):
    nombre = "Simpson 3/8 simple"
    categoria = "Integración"
    descripcion = "Aproxima la integral con un polinomio de grado 3 usando 4 puntos igualmente espaciados."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))

        f = crear_funcion(expresion)

        h = (b - a) / 3
        x0, x1, x2, x3 = a, a + h, a + 2 * h, b
        f0, f1, f2, f3 = f(x0), f(x1), f(x2), f(x3)
        resultado = (3 * h / 8) * (f0 + 3 * f1 + 3 * f2 + f3)

        pasos = [
            f"h = (b - a)/3 = {redondear(h)}",
            f"I = (3h/8)·(f0 + 3·f1 + 3·f2 + f3) = {redondear(resultado)}",
        ]

        tabla = [
            {"i": 0, "x": redondear(x0), "f(x)": redondear(f0), "peso": 1},
            {"i": 1, "x": redondear(x1), "f(x)": redondear(f1), "peso": 3},
            {"i": 2, "x": redondear(x2), "f(x)": redondear(f2), "peso": 3},
            {"i": 3, "x": redondear(x3), "f(x)": redondear(f3), "peso": 1},
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con Simpson 3/8 simple.",
            pasos=pasos,
            tabla=tabla,
        )
