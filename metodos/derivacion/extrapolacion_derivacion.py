import sympy as sp

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class ExtrapolacionDerivacion(MetodoNumerico):
    nombre = "Extrapolación en derivación"
    categoria = "Derivación"
    descripcion = (
        "Calcula f'(x) con alta precisión mediante extrapolación de Richardson. "
        "Parte de la diferencia central D(h) = [f(x+h) − f(x−h)] / (2h), cuyo "
        "error va en potencias pares de h, y la repite con pasos h, h/2, h/4, … "
        "Combinando esas estimaciones en una tabla triangular se cancelan "
        "sucesivamente los términos O(h²), O(h⁴), O(h⁶)…, acelerando mucho la "
        "convergencia. El mejor valor queda en la esquina de la tabla."
    )

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)",
         "tipo": "text", "placeholder": "sin(x)"},
        {"nombre": "x", "label": "Punto x donde derivar",
         "tipo": "number", "placeholder": "1"},
        {"nombre": "h", "label": "Paso inicial h",
         "tipo": "number", "placeholder": "0.4"},
        {"nombre": "niveles", "label": "Niveles de extrapolación",
         "tipo": "number", "placeholder": "4"},
    ]

    # ------------------------------------------------------------------ #
    #  Lógica del método                                                  #
    # ------------------------------------------------------------------ #
    def ejecutar(self, **kwargs):
        # ---- 1. Lectura y validación de parámetros ----
        funcion_txt = kwargs.get("funcion")
        if not funcion_txt or not str(funcion_txt).strip():
            return ResultadoMetodo(
                resultado=None,
                mensaje="Debes ingresar una función f(x).",
                pasos=[],
                tabla=[],
            )

        try:
            punto = float(kwargs.get("x"))
            h_raw = kwargs.get("h")
            h = float(h_raw) if h_raw not in (None, "") else 0.4
            niv_raw = kwargs.get("niveles")
            niveles = int(float(niv_raw)) if niv_raw not in (None, "") else 4
        except (TypeError, ValueError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="x y h deben ser números y los niveles un entero.",
                pasos=[],
                tabla=[],
            )

        if h == 0:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El paso h no puede ser 0.",
                pasos=[],
                tabla=[],
            )
        if niveles < 1:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El número de niveles debe ser al menos 1.",
                pasos=[],
                tabla=[],
            )

        # ---- 2. Parseo y evaluación de la función ----
        x = sp.symbols("x")
        try:
            expr = sp.sympify(str(funcion_txt).replace("^", "**"))
            f = sp.lambdify(x, expr, modules=["math"])
        except (sp.SympifyError, SyntaxError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje=f"No se pudo interpretar la función '{funcion_txt}'. "
                        "Usa sintaxis como x**2, sin(x), exp(x), log(x).",
                pasos=[],
                tabla=[],
            )

        # ---- 3. Primera columna: diferencia central con h, h/2, h/4, ... ----
        #   R[i][0] = D(h / 2^i)
        m = niveles + 1  # filas de la tabla (i = 0..niveles)
        R = [[None] * m for _ in range(m)]
        pasos_h = [h / (2 ** i) for i in range(m)]
        try:
            for i in range(m):
                hi = pasos_h[i]
                R[i][0] = (f(punto + hi) - f(punto - hi)) / (2 * hi)
        except (ValueError, ZeroDivisionError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="No se pudo evaluar la función en los puntos requeridos "
                        "(revisa el dominio: por ejemplo log o sqrt de negativos).",
                pasos=[],
                tabla=[],
            )

        # ---- 4. Extrapolación de Richardson ----
        #   R[i][j] = (4^j · R[i][j-1] − R[i-1][j-1]) / (4^j − 1)
        for j in range(1, m):
            for i in range(j, m):
                pot = 4 ** j
                R[i][j] = (pot * R[i][j - 1] - R[i - 1][j - 1]) / (pot - 1)

        mejor = R[m - 1][m - 1]

        # ---- 5. Derivada exacta y error ----
        try:
            derivada_exacta = float(sp.diff(expr, x).subs(x, punto))
            error_abs = abs(derivada_exacta - mejor)
            error_rel = (error_abs / abs(derivada_exacta)
                         if abs(derivada_exacta) > 1e-15 else None)
        except (TypeError, ValueError):
            derivada_exacta = None
            error_abs = None
            error_rel = None

        # ---- 6. Tabla triangular de Richardson ----
        encabezados = ["h"] + [f"O(h^{2 * (j + 1)})" for j in range(m)]
        # primera columna real es O(h^2); ajustamos etiquetas
        encabezados = ["paso h", "D(h)  O(h²)"] + \
                      [f"extrap. O(h^{2 * (j + 1)})" for j in range(1, m)]
        tabla = [encabezados]
        for i in range(m):
            fila = [round(pasos_h[i], 8)]
            for j in range(m):
                if R[i][j] is None:
                    fila.append("")
                else:
                    fila.append(round(R[i][j], 10))
            tabla.append(fila)

        # ---- 7. Pasos ----
        pasos = [
            f"Función: f(x) = {expr}.   Punto: x = {punto}.   "
            f"Paso inicial: h = {h}.   Niveles: {niveles}.",
            "Primera columna: diferencia central D(h) = [f(x+h) − f(x−h)]/(2h) "
            "evaluada con pasos h, h/2, h/4, …",
            "Como el error de D(h) va en potencias pares de h, se extrapola con "
            "la fórmula de Richardson:",
            "   R[i][j] = (4^j · R[i][j−1] − R[i−1][j−1]) / (4^j − 1)",
            "Cada columna j cancela el término O(h^(2j)) y mejora el orden "
            "(O(h²) → O(h⁴) → O(h⁶) …). Ver tabla.",
            f"Mejor estimación (esquina de la tabla): f'({punto}) ≈ {round(mejor, 10)}.",
        ]
        if derivada_exacta is not None:
            rel_txt = (f"{error_rel * 100:.3e} %" if error_rel is not None else "n/d")
            pasos.append(
                f"Derivada exacta f'({punto}) = {round(derivada_exacta, 10)}.  "
                f"Error absoluto = {error_abs:.3e};  error relativo = {rel_txt}."
            )

        # ---- 8. Resultado y mensaje ----
        resultado = {"derivada_aprox": round(mejor, 12)}
        if derivada_exacta is not None:
            resultado["derivada_exacta"] = round(derivada_exacta, 12)
            resultado["error_abs"] = error_abs

        mensaje = f"f'({punto}) ≈ {round(mejor, 10)}  (Richardson, {niveles} niveles)"
        if derivada_exacta is not None:
            mensaje += f"   |  exacta = {round(derivada_exacta, 8)}, error = {error_abs:.3e}"

        return ResultadoMetodo(
            resultado=resultado,
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )