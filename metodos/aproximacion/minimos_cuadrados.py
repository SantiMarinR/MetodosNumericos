from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class MinimosCuadrados(MetodoNumerico):
    nombre = "Mínimos cuadrados"
    categoria = "Aproximación"
    descripcion = (
        "Ajusta un polinomio de grado m a un conjunto de puntos (x, y) "
        "minimizando la suma de los cuadrados de los residuos. Con grado 1 "
        "obtiene la recta de regresión y = a0 + a1·x; con grados mayores ajusta "
        "parábolas, cúbicas, etc. Resuelve las ecuaciones normales."
    )

    parametros = [
        {"nombre": "xs", "label": "Valores de x (separados por coma)",
         "tipo": "text", "placeholder": "0, 1, 2, 3, 4"},
        {"nombre": "ys", "label": "Valores de y (separados por coma)",
         "tipo": "text", "placeholder": "1.1, 2.9, 5.2, 6.8, 9.1"},
        {"nombre": "grado", "label": "Grado del polinomio (1 = recta)",
         "tipo": "number", "placeholder": "1"},
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
        limpio = str(texto).replace(";", ",").replace(" ", ",")
        partes = [p for p in limpio.split(",") if p != ""]
        if not partes:
            raise ValueError("lista vacía")
        return [float(p) for p in partes]

    # ------------------------------------------------------------------ #
    #  Utilidad: resuelve A·c = b por eliminación de Gauss con pivoteo    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _resolver(A, b):
        n = len(A)
        # matriz aumentada
        M = [list(A[i]) + [b[i]] for i in range(n)]
        for col in range(n):
            # pivoteo parcial
            piv = max(range(col, n), key=lambda r: abs(M[r][col]))
            if abs(M[piv][col]) < 1e-12:
                raise ZeroDivisionError("sistema singular")
            M[col], M[piv] = M[piv], M[col]
            # eliminación
            for r in range(n):
                if r != col:
                    factor = M[r][col] / M[col][col]
                    for k in range(col, n + 1):
                        M[r][k] -= factor * M[col][k]
        return [M[i][n] / M[i][i] for i in range(n)]

    # ------------------------------------------------------------------ #
    #  Lógica del método                                                  #
    # ------------------------------------------------------------------ #
    def ejecutar(self, **kwargs):
        # ---- 1. Lectura y validación de parámetros ----
        try:
            xs = self._parse_lista(kwargs.get("xs"))
            ys = self._parse_lista(kwargs.get("ys"))
            grado_raw = kwargs.get("grado")
            grado = int(float(grado_raw)) if grado_raw not in (None, "") else 1
        except (TypeError, ValueError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Datos inválidos: x e y deben ser listas numéricas y "
                        "el grado un entero.",
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
        if grado < 1:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El grado debe ser un entero mayor o igual a 1.",
                pasos=[],
                tabla=[],
            )
        if n < grado + 1:
            return ResultadoMetodo(
                resultado=None,
                mensaje=f"Para un polinomio de grado {grado} se necesitan al "
                        f"menos {grado + 1} puntos (hay {n}).",
                pasos=[],
                tabla=[],
            )

        # ---- 2. Sumas de potencias para las ecuaciones normales ----
        #   S[p] = sum(x_i^p)        con p = 0 .. 2*grado
        #   T[q] = sum(y_i * x_i^q)  con q = 0 .. grado
        S = [sum(xi ** p for xi in xs) for p in range(2 * grado + 1)]
        T = [sum(ys[i] * xs[i] ** q for i in range(n)) for q in range(grado + 1)]

        # ---- 3. Construcción y resolución del sistema normal ----
        #   A[j][k] = S[j+k];  b[j] = T[j]
        m = grado + 1
        A = [[S[j + k] for k in range(m)] for j in range(m)]
        b = [T[j] for j in range(m)]
        try:
            coef = self._resolver(A, b)   # coef[0] + coef[1]x + coef[2]x^2 + ...
        except ZeroDivisionError:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El sistema no tiene solución única (puntos insuficientes "
                        "o x repetidos). Prueba con un grado menor o más puntos.",
                pasos=[],
                tabla=[],
            )

        # ---- 4. Predicciones, residuos y bondad de ajuste ----
        def predecir(x):
            return sum(coef[k] * x ** k for k in range(m))

        y_bar = sum(ys) / n
        ss_res = sum((ys[i] - predecir(xs[i])) ** 2 for i in range(n))
        ss_tot = sum((ys[i] - y_bar) ** 2 for i in range(n))
        r2 = (1 - ss_res / ss_tot) if ss_tot > 1e-15 else 1.0

        # ---- 5. Tabla de salida (primera fila = encabezados) ----
        tabla = [["i", "xi", "yi", "y estimado", "residuo (yi - ŷ)"]]
        for i in range(n):
            yhat = predecir(xs[i])
            tabla.append([
                i,
                round(xs[i], 6),
                round(ys[i], 6),
                round(yhat, 6),
                round(ys[i] - yhat, 6),
            ])

        # ---- 6. Polinomio en texto y pasos ----
        def termino(k):
            c = round(coef[k], 6)
            if k == 0:
                return f"{c}"
            if k == 1:
                return f"{c}*x"
            return f"{c}*x^{k}"

        polinomio = " + ".join(termino(k) for k in range(m))
        polinomio = polinomio.replace("+ -", "- ")  # estética: + -3 -> - 3

        ecuaciones = []
        for j in range(m):
            izq = " + ".join(
                f"a{k}*S{j + k}" for k in range(m)
            )
            ecuaciones.append(f"{izq} = T{j}")

        pasos = [
            f"Se reciben {n} puntos y se busca el polinomio de grado {grado} "
            f"que minimiza la suma de cuadrados de los residuos.",
            "Se calculan las sumas de potencias S_p = Σ x_i^p y "
            "T_q = Σ y_i·x_i^q.",
            "Se plantea el sistema de ecuaciones normales A·c = b, donde "
            "A[j][k] = S_(j+k) y b[j] = T_j:",
            *[f"   {ec}" for ec in ecuaciones],
            "Resolviendo por eliminación de Gauss se obtienen los coeficientes: "
            + ", ".join(f"a{k} = {round(coef[k], 6)}" for k in range(m)) + ".",
            f"Polinomio de ajuste:  y = {polinomio}.",
            f"Suma de cuadrados de residuos (SSres) = {round(ss_res, 6)}; "
            f"coeficiente de determinación R² = {round(r2, 6)}.",
        ]

        mensaje = f"Ajuste de grado {grado}:  y = {polinomio}   (R² = {round(r2, 6)})"

        return ResultadoMetodo(
            resultado=[round(c, 6) for c in coef],
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )