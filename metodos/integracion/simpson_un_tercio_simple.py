from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class SimpsonUnTercioSimple(MetodoNumerico):
    nombre = "Simpson 1/3 simple"
    categoria = "Integración"
    descripcion = "Aproxima la integral con una parábola que pasa por a, el punto medio y b."

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

        h = (b - a) / 2
        m = (a + b) / 2
        fa = f(a)
        fm = f(m)
        fb = f(b)
        resultado = (h / 3) * (fa + 4 * fm + fb)

        pasos = [
            f"h = (b - a)/2 = {redondear(h)}",
            f"punto medio = {redondear(m)}",
            f"I = (h/3)·(f(a) + 4·f(m) + f(b)) = {redondear(resultado)}",
        ]

        tabla = [
            {"i": 0, "x": redondear(a), "f(x)": redondear(fa), "peso": 1},
            {"i": 1, "x": redondear(m), "f(x)": redondear(fm), "peso": 4},
            {"i": 2, "x": redondear(b), "f(x)": redondear(fb), "peso": 1},
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con Simpson 1/3 simple.",
            pasos=pasos,
            tabla=tabla,
        )
