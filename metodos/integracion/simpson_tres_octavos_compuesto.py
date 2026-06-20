from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class SimpsonTresOctavosCompuesto(MetodoNumerico):
    nombre = "Simpson 3/8 compuesto"
    categoria = "Integración"
    descripcion = "Aplica Simpson 3/8 sobre n subintervalos (n debe ser múltiplo de 3)."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "n", "label": "Subintervalos n (múltiplo de 3)", "tipo": "number", "placeholder": "9"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        n = int(kwargs.get("n"))

        if n % 3 != 0 or n < 3:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Para Simpson 3/8 el número de subintervalos n debe ser múltiplo de 3.",
                pasos=[f"n = {n} no es válido. Usa un n múltiplo de 3 (3, 6, 9, ...)."],
                tabla=[],
            )

        f = crear_funcion(expresion)

        h = (b - a) / n
        suma = f(a) + f(b)
        tabla = [{"i": 0, "x": redondear(a), "f(x)": redondear(f(a)), "peso": 1}]

        for i in range(1, n):
            xi = a + i * h
            fxi = f(xi)
            peso = 2 if i % 3 == 0 else 3
            suma += peso * fxi
            tabla.append({"i": i, "x": redondear(xi), "f(x)": redondear(fxi), "peso": peso})

        tabla.append({"i": n, "x": redondear(b), "f(x)": redondear(f(b)), "peso": 1})

        resultado = (3 * h / 8) * suma

        pasos = [
            f"n = {n} (múltiplo de 3), h = (b - a)/n = {redondear(h)}",
            "Pesos: 1 en los extremos, 2 en índices múltiplos de 3, 3 en el resto.",
            f"I = (3h/8)·Σ(peso·f(x)) = {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con Simpson 3/8 compuesto.",
            pasos=pasos,
            tabla=tabla,
        )
