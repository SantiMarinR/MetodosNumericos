from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class Extrapolacion(MetodoNumerico):

    nombre = "Extrapolación"
    categoria = "Interpolación"

    descripcion = (
        "Estima el valor de una función en un punto fuera del rango "
        "de los datos conocidos utilizando el polinomio de Newton."
    )

    parametros = [
        {
            "nombre": "xs",
            "label": "Valores de x (separados por coma)",
            "placeholder": "1,2,3,4"
        },
        {
            "nombre": "ys",
            "label": "Valores de y (separados por coma)",
            "placeholder": "2,4,6,8"
        },
        {
            "nombre": "x",
            "label": "Punto a extrapolar",
            "placeholder": "5"
        }
    ]

    @staticmethod
    def _parse_lista(texto):

        if texto is None:
            raise ValueError("lista vacía")

        if isinstance(texto, (list, tuple)):
            return [float(v) for v in texto]

        limpio = str(texto).replace(";", ",").replace(" ", ",")

        partes = [p for p in limpio.split(",") if p != ""]

        if not partes:
            raise ValueError("lista vacía")

        return [float(p) for p in partes]

    def ejecutar(self, **kwargs):

        try:
            xs = self._parse_lista(kwargs.get("xs"))
            ys = self._parse_lista(kwargs.get("ys"))
            x = float(kwargs.get("x"))

        except (TypeError, ValueError):

            return ResultadoMetodo(
                resultado=None,
                mensaje="Datos inválidos.",
                pasos=[],
                tabla=[]
            )

        if len(xs) != len(ys):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Las listas deben tener el mismo tamaño.",
                pasos=[],
                tabla=[]
            )

        n = len(xs)

        if n < 2:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Se necesitan al menos 2 puntos.",
                pasos=[],
                tabla=[]
            )

        dd = [[0.0] * n for _ in range(n)]

        for i in range(n):
            dd[i][0] = ys[i]

        for j in range(1, n):
            for i in range(n - j):

                dd[i][j] = (
                    dd[i + 1][j - 1] - dd[i][j - 1]
                ) / (
                    xs[i + j] - xs[i]
                )

        coef = [dd[0][j] for j in range(n)]

        valor = coef[0]
        producto = 1

        for j in range(1, n):
            producto *= (x - xs[j - 1])
            valor += coef[j] * producto

        tabla = []

        for i in range(n):

            fila = {
                "i": i,
                "xi": round(xs[i], 6),
                "f(xi)": round(dd[i][0], 6)
            }

            tabla.append(fila)

        pasos = [
            f"Puntos utilizados: {n}",
            f"Valor extrapolado en x={x}",
            f"Resultado = {round(valor,6)}"
        ]

        return ResultadoMetodo(
            resultado=round(valor, 6),
            mensaje=f"P({x}) = {round(valor,6)}",
            pasos=pasos,
            tabla=tabla
        )