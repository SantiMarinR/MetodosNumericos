from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class CuadraturaAdaptativa(MetodoNumerico):
    nombre = "Cuadratura adaptativa"
    categoria = "Integración"
    descripcion = "Simpson adaptativo: subdivide el intervalo donde el error estimado supera la tolerancia."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "tolerancia", "label": "Tolerancia", "tipo": "number", "placeholder": "0.000001"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        tol = float(kwargs.get("tolerancia"))

        f = crear_funcion(expresion)

        def simpson_eval(fa, fb, fc, sub_a, sub_b):
            return (abs(sub_b - sub_a) / 6) * (fa + 4 * fc + fb)

        def paso_adaptativo(sub_a, sub_b, tol_actual, fa, fb, fc):
            c = (sub_a + sub_b) / 2
            d = (sub_a + c) / 2
            e = (c + sub_b) / 2
            fd = f(d)
            fe = f(e)
            s1 = simpson_eval(fa, fb, fc, sub_a, sub_b)
            s2 = simpson_eval(fa, fc, fd, sub_a, c) + simpson_eval(fc, fb, fe, c, sub_b)
            if abs(s2 - s1) <= 15 * tol_actual:
                return s2 + (s2 - s1) / 15
            return (paso_adaptativo(sub_a, c, tol_actual / 2, fa, fc, fd) +
                    paso_adaptativo(c, sub_b, tol_actual / 2, fc, fb, fe))

        fa, fb = f(a), f(b)
        c = (a + b) / 2
        fc = f(c)
        resultado = paso_adaptativo(a, b, tol, fa, fb, fc)

        pasos = [
            f"Intervalo inicial: [{a}, {b}]",
            f"Tolerancia: {tol}",
            "Se aplica Simpson y se compara con la suma de dos mitades; si el error estimado",
            "supera 15·tolerancia, el subintervalo se divide recursivamente.",
            f"I ≈ {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con cuadratura adaptativa.",
            pasos=pasos,
            tabla=[],
        )
