from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


# Nodos y pesos de Gauss-Legendre en el intervalo de referencia [-1, 1]
GAUSS_DATA = {
    2: ([-0.5773502691896257, 0.5773502691896257],
        [1.0, 1.0]),
    3: ([-0.7745966692414834, 0.0, 0.7745966692414834],
        [0.5555555555555556, 0.8888888888888888, 0.5555555555555556]),
    4: ([-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526],
        [0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538]),
    5: ([-0.9061798459386640, -0.5384693101056831, 0.0, 0.5384693101056831, 0.9061798459386640],
        [0.2369268850561891, 0.4786286704993665, 0.5688888888888889, 0.4786286704993665, 0.2369268850561891]),
}


class LegendreCompuesto(MetodoNumerico):
    nombre = "Cuadratura de Gauss-Legendre compuesta"
    categoria = "Integración"
    descripcion = "Divide [a, b] en n subintervalos y aplica Gauss-Legendre en cada uno."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "puntos", "label": "Número de puntos (2 a 5)", "tipo": "number", "placeholder": "3"},
        {"nombre": "n", "label": "Número de subintervalos n", "tipo": "number", "placeholder": "4"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        puntos = int(kwargs.get("puntos"))
        n = int(kwargs.get("n"))

        if puntos not in GAUSS_DATA:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Número de puntos no soportado. Usa 2, 3, 4 o 5.",
                pasos=[f"puntos = {puntos} no es válido."],
                tabla=[],
            )
        if n < 1:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El número de subintervalos n debe ser al menos 1.",
                pasos=[f"n = {n} no es válido."],
                tabla=[],
            )

        f = crear_funcion(expresion)
        nodos, pesos = GAUSS_DATA[puntos]

        h = (b - a) / n
        integral_total = 0.0
        tabla = []

        for i in range(n):
            sub_a = a + i * h
            sub_b = sub_a + h
            suma_sub = 0.0
            for nodo, peso in zip(nodos, pesos):
                x_trans = 0.5 * ((sub_b - sub_a) * nodo + (sub_b + sub_a))
                suma_sub += peso * f(x_trans)
            parcial = 0.5 * (sub_b - sub_a) * suma_sub
            integral_total += parcial
            tabla.append({
                "subintervalo": i + 1,
                "a_i": redondear(sub_a),
                "b_i": redondear(sub_b),
                "integral parcial": redondear(parcial),
            })

        pasos = [
            f"n = {n} subintervalos, h = (b - a)/n = {redondear(h)}",
            f"Puntos de Gauss por subintervalo: {puntos}",
            "En cada subintervalo se transforman los nodos de [-1,1] a [a_i, b_i].",
            f"I = Σ(integrales parciales) = {redondear(integral_total)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(integral_total),
            mensaje="Integral aproximada con Gauss-Legendre compuesta.",
            pasos=pasos,
            tabla=tabla,
        )