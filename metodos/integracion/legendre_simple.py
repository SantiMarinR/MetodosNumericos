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


class LegendreSimple(MetodoNumerico):
    nombre = "Cuadratura de Gauss-Legendre simple"
    categoria = "Integración"
    descripcion = "Aproxima la integral con nodos y pesos de Gauss-Legendre sobre todo el intervalo [a, b]."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Límite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Límite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "puntos", "label": "Número de puntos (2 a 5)", "tipo": "number", "placeholder": "3"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        puntos = int(kwargs.get("puntos"))

        if puntos not in GAUSS_DATA:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Número de puntos no soportado. Usa 2, 3, 4 o 5.",
                pasos=[f"puntos = {puntos} no es válido."],
                tabla=[],
            )

        f = crear_funcion(expresion)
        nodos, pesos = GAUSS_DATA[puntos]

        suma = 0.0
        tabla = []
        for k, (nodo, peso) in enumerate(zip(nodos, pesos), start=1):
            # Cambio de variable de [-1, 1] a [a, b]
            x_trans = 0.5 * ((b - a) * nodo + (b + a))
            fx = f(x_trans)
            suma += peso * fx
            tabla.append({
                "k": k,
                "nodo (-1,1)": redondear(nodo),
                "peso": redondear(peso),
                "x en [a,b]": redondear(x_trans),
                "f(x)": redondear(fx),
            })

        resultado = 0.5 * (b - a) * suma

        pasos = [
            f"Puntos de Gauss: {puntos}",
            "Cada nodo se transforma de [-1,1] a [a,b] con x = 0.5·((b-a)·t + (b+a)).",
            f"I = 0.5·(b - a)·Σ(peso·f(x)) = {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con Gauss-Legendre simple.",
            pasos=pasos,
            tabla=tabla,
        )
