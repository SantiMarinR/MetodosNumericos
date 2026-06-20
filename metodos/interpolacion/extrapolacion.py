from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class Extrapolacion(MetodoNumerico):
    nombre = "Extrapolación"
    categoria = "Interpolación"
    descripcion = (
        "Estima el valor de una función en un punto que cae FUERA del rango de "
        "los datos conocidos. Construye el polinomio interpolante de Newton "
        "(diferencias divididas) a partir de los puntos dados y lo evalúa en el "
        "punto solicitado."
    )

    parametros = [
        {"nombre": "xs", "label": "Valores de x (separados por coma)",
         "tipo": "text", "placeholder": "1, 2, 3, 4"},
        {"nombre": "ys", "label": "Valores de y = f(x) (separados por coma)",
         "tipo": "text", "placeholder": "0, 0.6931, 1.0986, 1.3863"},
        {"nombre": "x", "label": "Punto a extrapolar",
         "tipo": "number", "placeholder": "5"},
    ]

    # ------------------------------------------------------------------ #
    #  Utilidad: convierte un texto "1, 2, 3" en una lista de floats      #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_lista(texto):
        if texto is None:
            raise ValueError("lista vacía")
        if isinstance(texto, (list, tuple)):
            return [float(v) for v in texto]
        # admite coma, punto y coma o espacios como separadores
        limpio = str(texto).replace(";", ",").replace(" ", ",")
        partes = [p for p in limpio.split(",") if p != ""]
        if not partes:
            raise ValueError("lista vacía")
        return [float(p) for p in partes]

    # ------------------------------------------------------------------ #
    #  Lógica del método                                                  #
    # ------------------------------------------------------------------ #
    def ejecutar(self, **kwargs):
        # ---- 1. Lectura y validación de parámetros ----
        try:
            xs = self._parse_lista(kwargs.get("xs"))
            ys = self._parse_lista(kwargs.get("ys"))
            x = float(kwargs.get("x"))
        except (TypeError, ValueError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Datos inválidos: x e y deben ser listas numéricas y "
                        "el punto a extrapolar un número.",
                pasos=[],
                tabla=[],
            )

        if len(xs) != len(ys):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Las listas de x e y deben tener la misma cantidad de valores.",
                pasos=[],
                tabla=[],
            )

        n = len(xs)
        if n < 2:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Se necesitan al menos 2 puntos para construir el polinomio.",
                pasos=[],
                tabla=[],
            )

        if len(set(xs)) != n:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Los valores de x deben ser distintos entre sí.",
                pasos=[],
                tabla=[],
            )

        # ---- 2. Tabla de diferencias divididas de Newton ----
        #   dd[i][j] = f[x_i, ..., x_{i+j}]
        dd = [[0.0] * n for _ in range(n)]
        for i in range(n):
            dd[i][0] = ys[i]
        for j in range(1, n):
            for i in range(n - j):
                dd[i][j] = (dd[i + 1][j - 1] - dd[i][j - 1]) / (xs[i + j] - xs[i])

        # Coeficientes del polinomio = primera fila de la tabla
        coef = [dd[0][j] for j in range(n)]

        # ---- 3. Evaluación en el punto pedido ----
        #   P(x) = c0 + c1(x-x0) + c2(x-x0)(x-x1) + ...
        valor = coef[0]
        producto = 1.0
        for j in range(1, n):
            producto *= (x - xs[j - 1])
            valor += coef[j] * producto

        # ---- 4. Armado de la tabla de salida (lista de filas) ----
        #   Primera fila = encabezados. Si tu plantilla maneja los
        #   encabezados aparte, basta con quitar esta primera fila.
        encabezados = ["i", "xi", "f[xi]"] + [f"orden {j}" for j in range(1, n)]
        tabla = [encabezados]
        for i in range(n):
            fila = [i, round(xs[i], 6), round(dd[i][0], 6)]
            for j in range(1, n):
                fila.append(round(dd[i][j], 6) if i < n - j else "")
            tabla.append(fila)

        # ---- 5. Pasos explicativos ----
        dentro = min(xs) <= x <= max(xs)
        tipo = ("interpolación (el punto cae DENTRO del rango)" if dentro
                else "extrapolación (el punto cae FUERA del rango)")

        terminos = " + ".join(
            "c0" if j == 0 else f"c{j}" + "".join(f"(x-x{k})" for k in range(j))
            for j in range(n)
        )
        coefs_txt = ", ".join(f"c{j} = {round(coef[j], 6)}" for j in range(n))

        pasos = [
    "DATOS INGRESADOS",
    ", ".join(f"({xs[i]}, {ys[i]})" for i in range(n)),

    "",

    "ANÁLISIS DEL PUNTO",
    f"Rango de x: [{min(xs)}, {max(xs)}]",
    f"Punto solicitado: x = {x}",
    f"Tipo de cálculo: {tipo}",

    "",

    "TABLA DE DIFERENCIAS DIVIDIDAS",
    "Los coeficientes se obtienen de la primera fila de la tabla.",

    "",

    "COEFICIENTES DEL POLINOMIO",
    coefs_txt,

    "",

    "POLINOMIO DE NEWTON",
    f"P(x) = {terminos}",

    "",

    "EVALUACIÓN",
    f"P({x}) = {round(valor, 6)}",
]

        accion = "interpola" if dentro else "extrapola"
        mensaje = (
    f"RESULTADO FINAL\n\n"
    f"x = {x}\n"
    f"P(x) = {round(valor,6)}"
)

        return ResultadoMetodo(
            resultado=round(valor, 6),
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )