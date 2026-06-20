import sympy as sp

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class TresPuntos(MetodoNumerico):
    nombre = "Derivación por 3 puntos"
    categoria = "Derivación"
    descripcion = (
        "Aproxima la primera derivada f'(x) usando tres puntos separados un "
        "paso h, con error de truncamiento O(h²). Soporta la fórmula central "
        "[f(x+h) − f(x−h)] / (2h) y las versiones de extremo hacia adelante "
        "[−3f(x) + 4f(x+h) − f(x+2h)] / (2h) y hacia atrás "
        "[3f(x) − 4f(x−h) + f(x−2h)] / (2h). Compara con la derivada exacta "
        "para mostrar el error."
    )

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)",
         "tipo": "text", "placeholder": "sin(x)"},
        {"nombre": "x", "label": "Punto x donde derivar",
         "tipo": "number", "placeholder": "1"},
        {"nombre": "h", "label": "Paso h",
         "tipo": "number", "placeholder": "0.1"},
        {"nombre": "formula", "label": "Fórmula: central / adelante / atras",
         "tipo": "text", "placeholder": "central"},
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
            h = float(h_raw) if h_raw not in (None, "") else 0.1
        except (TypeError, ValueError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="x y h deben ser números.",
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

        formula = str(kwargs.get("formula") or "central").strip().lower()
        if formula in ("adelante", "forward", "progresiva", "hacia adelante"):
            formula = "adelante"
        elif formula in ("atras", "atrás", "backward", "regresiva", "hacia atras"):
            formula = "atras"
        else:
            formula = "central"

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

        # ---- 3. Nodos y coeficientes según la fórmula ----
        #   f'(x) ≈ (1/(2h)) * Σ coef_i * f(x + d_i*h)
        if formula == "adelante":
            desplazamientos = [0, 1, 2]
            coefs = [-3, 4, -1]
            etiquetas = ["x", "x + h", "x + 2h"]
            formula_txt = "[−3 f(x) + 4 f(x+h) − f(x+2h)] / (2h)"
        elif formula == "atras":
            desplazamientos = [0, -1, -2]
            coefs = [3, -4, 1]
            etiquetas = ["x", "x − h", "x − 2h"]
            formula_txt = "[3 f(x) − 4 f(x−h) + f(x−2h)] / (2h)"
        else:  # central
            desplazamientos = [-1, 1]
            coefs = [-1, 1]
            etiquetas = ["x − h", "x + h"]
            formula_txt = "[f(x+h) − f(x−h)] / (2h)"

        # ---- 4. Evaluación en los nodos y cálculo de la derivada ----
        try:
            valores = [f(punto + d * h) for d in desplazamientos]
        except (ValueError, ZeroDivisionError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="No se pudo evaluar la función en los puntos requeridos "
                        "(revisa el dominio: por ejemplo log o sqrt de negativos).",
                pasos=[],
                tabla=[],
            )

        numerador = sum(c * v for c, v in zip(coefs, valores))
        derivada = numerador / (2 * h)

        # ---- 5. Derivada exacta y error ----
        try:
            derivada_exacta = float(sp.diff(expr, x).subs(x, punto))
            error_abs = abs(derivada_exacta - derivada)
            error_rel = (error_abs / abs(derivada_exacta)
                         if abs(derivada_exacta) > 1e-15 else None)
        except (TypeError, ValueError):
            derivada_exacta = None
            error_abs = None
            error_rel = None

        # ---- 6. Tabla con los puntos usados ----
        tabla = [["punto", "coef", "valor de x", "f(x)"]]
        for etiqueta, c, d, v in zip(etiquetas, coefs, desplazamientos, valores):
            tabla.append([etiqueta, c, round(punto + d * h, 8), round(v, 8)])

        # ---- 7. Pasos ----
        nombre_formula = {"adelante": "3 puntos hacia adelante",
                          "atras": "3 puntos hacia atrás",
                          "central": "3 puntos central"}[formula]
        # nota: la "central" usa solo 2 evaluaciones porque el coeficiente de f(x) es 0
        nota_central = (" (el coeficiente de f(x) es 0, por eso solo aparecen "
                        "dos evaluaciones)" if formula == "central" else "")
        pasos = [
            f"Función: f(x) = {expr}.   Punto: x = {punto}.   Paso: h = {h}.",
            f"Fórmula elegida: {nombre_formula}, con error de truncamiento O(h²):",
            f"   f'(x) ≈ {formula_txt}{nota_central}",
            "Se evalúa la función en los nodos y se combinan con sus coeficientes "
            "(ver tabla).",
            f"Numerador = Σ coef·f = {round(numerador, 8)};  "
            f"f'({punto}) ≈ {round(numerador, 8)} / (2·{h}) = {round(derivada, 8)}.",
        ]
        if derivada_exacta is not None:
            rel_txt = (f"{round(error_rel * 100, 6)} %"
                       if error_rel is not None else "n/d")
            pasos.append(
                f"Derivada exacta f'({punto}) = {round(derivada_exacta, 8)}.  "
                f"Error absoluto = {error_abs:.3e};  error relativo = {rel_txt}."
            )
            tabla.append(["—", "", "f'(x) aproximada", round(derivada, 8)])
            tabla.append(["—", "", "f'(x) exacta", round(derivada_exacta, 8)])
            tabla.append(["—", "", "error absoluto", round(error_abs, 12)])

        # ---- 8. Resultado y mensaje ----
        resultado = {"derivada_aprox": round(derivada, 10), "formula": formula}
        if derivada_exacta is not None:
            resultado["derivada_exacta"] = round(derivada_exacta, 10)
            resultado["error_abs"] = error_abs

        mensaje = f"f'({punto}) ≈ {round(derivada, 10)}  ({nombre_formula}, O(h²))"
        if derivada_exacta is not None:
            mensaje += f"   |  exacta = {round(derivada_exacta, 8)}, error = {error_abs:.3e}"

        return ResultadoMetodo(
            resultado=resultado,
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )