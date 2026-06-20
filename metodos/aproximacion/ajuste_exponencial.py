import math

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class AjusteExponencial(MetodoNumerico):
    nombre = "Ajuste exponencial"
    categoria = "Aproximación"
    descripcion = (
        "Ajusta una curva de la forma y = a·e^(b·x) a un conjunto de puntos "
        "(x, y). Se lineariza tomando logaritmo natural: ln(y) = ln(a) + b·x, "
        "lo que convierte el problema en una regresión lineal Y = A + b·x "
        "(con Y = ln(y), A = ln(a)) resuelta por mínimos cuadrados. "
        "Al final se recupera a = e^A. Requiere y > 0."
    )

    parametros = [
        {"nombre": "xs", "label": "Valores de x (separados por coma)",
         "tipo": "text", "placeholder": "0, 1, 2, 3, 4"},
        {"nombre": "ys", "label": "Valores de y (separados por coma, y > 0)",
         "tipo": "text", "placeholder": "1.0, 2.1, 4.0, 8.2, 15.9"},
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

        if any(yi <= 0 for yi in ys):
            return ResultadoMetodo(
                resultado=None,
                mensaje="Todos los valores de y deben ser positivos (y > 0), "
                        "ya que la linealización usa ln(y).",
                pasos=[],
                tabla=[],
            )

        # ---- 2. Linealización: Y = ln(y), el modelo es Y = A + b·x ----
        Y = [math.log(yi) for yi in ys]

        # ---- 3. Sumas para las ecuaciones normales de la recta ----
        sum_x = sum(xs)
        sum_Y = sum(Y)
        sum_xx = sum(xi * xi for xi in xs)
        sum_xY = sum(xs[i] * Y[i] for i in range(n))

        denom = n * sum_xx - sum_x * sum_x
        if abs(denom) < 1e-15:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El sistema no tiene solución única (los valores de x "
                        "son iguales o casi iguales).",
                pasos=[],
                tabla=[],
            )

        # b = pendiente, A = intercepto en el espacio linealizado
        b = (n * sum_xY - sum_x * sum_Y) / denom
        A = (sum_Y - b * sum_x) / n
        a = math.exp(A)   # se recupera el coeficiente original

        # ---- 4. Predicciones, residuos y bondad de ajuste (en y real) ----
        def predecir(x):
            return a * math.exp(b * x)

        y_bar = sum(ys) / n
        ss_res = sum((ys[i] - predecir(xs[i])) ** 2 for i in range(n))
        ss_tot = sum((ys[i] - y_bar) ** 2 for i in range(n))
        r2 = (1 - ss_res / ss_tot) if ss_tot > 1e-15 else 1.0

        # ---- 5. Tabla de salida (primera fila = encabezados) ----
        tabla = [["i", "xi", "yi", "Y = ln(yi)", "y estimado", "residuo (yi - ŷ)"]]
        for i in range(n):
            yhat = predecir(xs[i])
            tabla.append([
                i,
                round(xs[i], 6),
                round(ys[i], 6),
                round(Y[i], 6),
                round(yhat, 6),
                round(ys[i] - yhat, 6),
            ])

        # ---- 6. Modelo en texto y pasos ----
        signo = "" if b >= 0 else "-"
        modelo = f"y = {round(a, 6)}*e^({signo}{round(abs(b), 6)}*x)"

        pasos = [
            f"Se reciben {n} puntos y se busca el modelo y = a·e^(b·x).",
            "Se toma logaritmo natural a ambos lados: ln(y) = ln(a) + b·x. "
            "Con Y = ln(y) y A = ln(a) queda la recta Y = A + b·x.",
            f"Se calculan las sumas:  Σx = {round(sum_x, 6)},  ΣY = {round(sum_Y, 6)}, "
            f" Σx² = {round(sum_xx, 6)},  Σx·Y = {round(sum_xY, 6)}.",
            "Se resuelven las ecuaciones normales de la recta:",
            f"   b = (n·Σx·Y − Σx·ΣY) / (n·Σx² − (Σx)²) = {round(b, 6)}",
            f"   A = (ΣY − b·Σx) / n = {round(A, 6)}",
            f"Se recupera el coeficiente original:  a = e^A = e^{round(A, 6)} = {round(a, 6)}.",
            f"Modelo de ajuste:  {modelo}.",
            f"Suma de cuadrados de residuos (SSres, en y real) = {round(ss_res, 6)}; "
            f"coeficiente de determinación R² = {round(r2, 6)}.",
        ]

        mensaje = f"Ajuste exponencial:  {modelo}   (R² = {round(r2, 6)})"

        return ResultadoMetodo(
            resultado={"a": round(a, 6), "b": round(b, 6), "r2": round(r2, 6)},
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )