from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class TrapecioSimple(MetodoNumerico):
    nombre = "Trapecio simple"
    categoria = "Integración"
    descripcion = "Aproxima la integral con un solo trapecio usando los extremos del intervalo [a, b]."

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

        h = b - a
        fa = f(a)
        fb = f(b)
        resultado = (h / 2) * (fa + fb)

        pasos = [
            f"h = b - a = {redondear(h)}",
            f"f(a) = f({a}) = {redondear(fa)}",
            f"f(b) = f({b}) = {redondear(fb)}",
            f"I = (h/2)·(f(a) + f(b)) = {redondear(resultado)}",
        ]

        tabla = [
            {"i": 0, "x": redondear(a), "f(x)": redondear(fa), "peso": 1},
            {"i": 1, "x": redondear(b), "f(x)": redondear(fb), "peso": 1},
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con trapecio simple.",
            pasos=pasos,
            tabla=tabla,
        )