from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class TrapecioCompuesto(MetodoNumerico):
    nombre = "Trapecio compuesto"
    categoria = "Integración"
    descripcion = "Divide [a, b] en n subintervalos y suma el área de n trapecios."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "n", "label": "Número de subintervalos n", "tipo": "number", "placeholder": "6"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        n = int(kwargs.get("n"))

        if n < 1:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El número de subintervalos n debe ser al menos 1.",
                pasos=["Corrige el valor de n."],
                tabla=[],
            )

        f = crear_funcion(expresion)

        h = (b - a) / n
        suma = f(a) + f(b)
        tabla = []

        fa = f(a)
        tabla.append({"i": 0, "x": redondear(a), "f(x)": redondear(fa), "peso": 1})

        for i in range(1, n):
            xi = a + i * h
            fxi = f(xi)
            suma += 2 * fxi
            tabla.append({"i": i, "x": redondear(xi), "f(x)": redondear(fxi), "peso": 2})

        fb = f(b)
        tabla.append({"i": n, "x": redondear(b), "f(x)": redondear(fb), "peso": 1})

        resultado = (h / 2) * suma

        pasos = [
            f"n = {n}, h = (b - a)/n = {redondear(h)}",
            "Pesos: 1 en los extremos, 2 en los puntos interiores.",
            f"I = (h/2)·Σ(peso·f(x)) = {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con trapecio compuesto.",
            pasos=pasos,
            tabla=tabla,
        )
