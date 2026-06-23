from core.funciones import crear_funcion, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


GAUSS_DATA = {
    2: ([-0.5773502691896257, 0.5773502691896257], [1.0, 1.0]),
    3: ([-0.7745966692414834, 0.0, 0.7745966692414834], [0.5555555555555556, 0.8888888888888888, 0.5555555555555556]),
    4: ([-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526], [0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538]),
    5: ([-0.9061798459386640, -0.5384693101056831, 0.0, 0.5384693101056831, 0.9061798459386640], [0.2369268850561891, 0.4786286704993665, 0.5688888888888889, 0.4786286704993665, 0.2369268850561891]),
}


class LegendreSimple(MetodoNumerico):
    nombre = "Cuadratura de Gauss-Legendre simple"
    categoria = "Integración"
    descripcion = "Aproxima la integral con nodos y pesos de Gauss-Legendre sobre todo el intervalo [a, b]."

    parametros = [
        {"nombre": "funcion", "label": "Funcion f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Limite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Limite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "puntos", "label": "Numero de puntos (2 a 5)", "tipo": "number", "placeholder": "3"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        puntos = int(kwargs.get("puntos"))

        if puntos not in GAUSS_DATA:
            return ResultadoMetodo(None, "Numero de puntos no soportado. Usa 2, 3, 4 o 5.", [f"puntos = {puntos} no es valido."], [])

        f = crear_funcion(expresion)
        nodos, pesos = GAUSS_DATA[puntos]

        suma = 0.0
        tabla = []
        pasos = [
            f"Puntos de Gauss: {puntos}.",
            "Se transforma cada nodo t de [-1,1] al intervalo [a,b] con x = 0.5*((b-a)*t + (b+a)).",
        ]
        for k, (nodo, peso) in enumerate(zip(nodos, pesos), start=1):
            x_trans = 0.5 * ((b - a) * nodo + (b + a))
            fx = f(x_trans)
            aporte = peso * fx
            suma += aporte
            tabla.append({
                "k": k,
                "nodo t": redondear(nodo),
                "peso w": redondear(peso),
                "x en [a,b]": redondear(x_trans),
                "f(x)": redondear(fx),
                "w*f(x)": redondear(aporte),
            })
            pasos.append(
                f"Nodo {k}: x=0.5*(({redondear(b)}-{redondear(a)})*{redondear(nodo)}+({redondear(b)}+{redondear(a)}))={redondear(x_trans)}; "
                f"w*f(x)={redondear(peso)}*{redondear(fx)}={redondear(aporte)}."
            )

        resultado = 0.5 * (b - a) * suma
        pasos.append(
            f"I = 0.5*(b-a)*suma = 0.5*({redondear(b)}-{redondear(a)})*{redondear(suma)} = {redondear(resultado)}."
        )

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral aproximada con Gauss-Legendre simple.",
            pasos=pasos,
            tabla=tabla,
        )
