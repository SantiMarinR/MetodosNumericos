from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class SimpsonUnTercioCompuesto(MetodoNumerico):
    nombre = "Simpson 1/3 compuesto"
    categoria = "Integración"
    descripcion = "Aplica Simpson 1/3 sobre n subintervalos (n debe ser par)."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "n", "label": "Subintervalos n (par)", "tipo": "number", "placeholder": "6"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        n = int(kwargs.get("n"))

        if n % 2 != 0 or n < 2:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Para Simpson 1/3 el número de subintervalos n debe ser par y mayor o igual a 2.",
                pasos=[f"n = {n} no es válido. Usa un n par (2, 4, 6, ...)."],
                tabla=[],
            )

        f = crear_funcion(expresion)

        h = (b - a) / n
        suma = f(a) + f(b)
        tabla = [{"i": 0, "x": redondear(a), "f(x)": redondear(f(a)), "peso": 1}]

        for i in range(1, n):
            xi = a + i * h
            fxi = f(xi)
            peso = 2 if i % 2 == 0 else 4
            suma += peso * fxi
            tabla.append({"i": i, "x": redondear(xi), "f(x)": redondear(fxi), "peso": peso})

        tabla.append({"i": n, "x": redondear(b), "f(x)": redondear(f(b)), "peso": 1})

        resultado = (h / 3) * suma

        pasos = [
            f"n = {n} (par), h = (b - a)/n = {redondear(h)}",
            "Pesos: 1 en los extremos, 4 en índices impares, 2 en índices pares interiores.",
            f"I = (h/3)·Σ(peso·f(x)) = {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con Simpson 1/3 compuesto.",
            pasos=pasos,
            tabla=tabla,
        )
