import math

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class AjusteLogaritmico(MetodoNumerico):
    nombre = "Ajuste logarítmico"
    categoria = "Aproximación"
    descripcion = (
        "Ajusta una curva de la forma y = a + b·ln(x) a un conjunto de puntos "
        "(x, y). Se lineariza con el cambio de variable X = ln(x), lo que "
        "convierte el problema en una regresión lineal y = a + b·X resuelta "
        "por mínimos cuadrados. Requiere x > 0."
    )

    parametros = [
        {"nombre": "xs", "label": "Valores de x (separados por coma, x > 0)",
         "tipo": "text", "placeholder": "1, 2, 3, 4, 5"},
        {"nombre": "ys", "label": "Valores de y (separados por coma)",
         "tipo": "text", "placeholder": "0.5, 2.1, 2.9, 3.5, 4.0"},
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
    #  Lógica del método                                                  #
    # ------------------------------------------------------------------ #
    def ejecutar(self, **kwargs):
        # ---- 1. Lectura y validación de parámetros ----
        try:
            xs = self._parse_lista(kwargs.get("xs"))
            ys = self._parse_lista(kwargs.get("ys"))
        except (TypeError, ValueError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Datos inválidos: x e y deben ser listas numéricas.",
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
                mensaje="Se necesitan al menos 2 puntos para ajustar la curva.",
                pasos=[],
                tabla=[],
            )

        if any(xi <= 0 for xi in xs):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Todos los valores de x deben ser positivos (x > 0), "
                        "ya que el modelo usa ln(x).",
                pasos=[],
                tabla=[],
            )

        # ---- 2. Linealización: X = ln(x), el modelo es y = a + b·X ----
        X = [math.log(xi) for xi in xs]

        # ---- 3. Sumas para las ecuaciones normales de la recta ----
        sum_X = sum(X)
        sum_y = sum(ys)
        sum_XX = sum(Xi * Xi for Xi in X)
        sum_Xy = sum(X[i] * ys[i] for i in range(n))

        denom = n * sum_XX - sum_X * sum_X
        if abs(denom) < 1e-15:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El sistema no tiene solución única (los valores de x "
                        "producen ln(x) iguales o casi iguales).",
                pasos=[],
                tabla=[],
            )

        # b = pendiente, a = intercepto
        b = (n * sum_Xy - sum_X * sum_y) / denom
        a = (sum_y - b * sum_X) / n

        # ---- 4. Predicciones, residuos y bondad de ajuste ----
        def predecir(x):
            return a + b * math.log(x)

        y_bar = sum_y / n
        ss_res = sum((ys[i] - predecir(xs[i])) ** 2 for i in range(n))
        ss_tot = sum((ys[i] - y_bar) ** 2 for i in range(n))
        r2 = (1 - ss_res / ss_tot) if ss_tot > 1e-15 else 1.0

        # ---- 5. Tabla de salida (primera fila = encabezados) ----
        tabla = [["i", "xi", "X = ln(xi)", "yi", "y estimado", "residuo (yi - ŷ)"]]
        for i in range(n):
            yhat = predecir(xs[i])
            tabla.append([
                i,
                round(xs[i], 6),
                round(X[i], 6),
                round(ys[i], 6),
                round(yhat, 6),
                round(ys[i] - yhat, 6),
            ])

        # ---- 6. Modelo en texto y pasos ----
        signo = "+" if b >= 0 else "-"
        modelo = f"y = {round(a, 6)} {signo} {round(abs(b), 6)}*ln(x)"

        pasos = [
            f"Se reciben {n} puntos y se busca el modelo y = a + b·ln(x).",
            "Se lineariza con el cambio X = ln(x), de modo que el modelo se "
            "vuelve una recta: y = a + b·X.",
            f"Se calculan las sumas:  ΣX = {round(sum_X, 6)},  Σy = {round(sum_y, 6)}, "
            f" ΣX² = {round(sum_XX, 6)},  ΣX·y = {round(sum_Xy, 6)}.",
            "Se resuelven las ecuaciones normales de la recta:",
            f"   b = (n·ΣX·y − ΣX·Σy) / (n·ΣX² − (ΣX)²) = {round(b, 6)}",
            f"   a = (Σy − b·ΣX) / n = {round(a, 6)}",
            f"Modelo de ajuste:  {modelo}.",
            f"Suma de cuadrados de residuos (SSres) = {round(ss_res, 6)}; "
            f"coeficiente de determinación R² = {round(r2, 6)}.",
        ]

        mensaje = f"Ajuste logarítmico:  {modelo}   (R² = {round(r2, 6)})"

        return ResultadoMetodo(
            resultado={"a": round(a, 6), "b": round(b, 6), "r2": round(r2, 6)},
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )