from metodos.integracion.legendre_simple import LegendreSimple


class CuadraturaGaussiana(LegendreSimple):
    nombre = "Cuadratura gaussiana"
    descripcion = (
        "Aproxima la integral con cuadratura gaussiana de Gauss-Legendre, "
        "transformando los nodos de [-1, 1] al intervalo [a, b]."
    )
