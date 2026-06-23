import sympy as sp

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_expresion


class DosPuntos(MetodoNumerico):
    nombre = "Derivación por 2 puntos"
    categoria = "Derivación"
    descripcion = (
        "Aproxima la primera derivada f'(x) usando dos puntos separados un paso "
        "h. Soporta tres fórmulas: adelante  [f(x+h) − f(x)] / h, "
        "atrás  [f(x) − f(x−h)] / h  (ambas con error O(h)), y central "
        "[f(x+h) − f(x−h)] / (2h)  (error O(h²), más exacta). Compara el "
        "resultado con la derivada exacta para mostrar el error."
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
        # normalización de sinónimos
        if formula in ("adelante", "forward", "progresiva", "hacia adelante"):
            formula = "adelante"
        elif formula in ("atras", "atrás", "backward", "regresiva", "hacia atras"):
            formula = "atras"
        else:
            formula = "central"

        # ---- 2. Parseo y evaluación de la función ----
        try:
            x, expr = crear_expresion(funcion_txt)
            f = sp.lambdify(x, expr, modules=["math"])
        except (sp.SympifyError, SyntaxError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje=f"No se pudo interpretar la función '{funcion_txt}'. "
                        "Usa sintaxis como x**2, sin(x), exp(x), log(x).",
                pasos=[],
                tabla=[],
            )

        try:
            if formula == "adelante":
                f_x = f(punto)
                f_mas = f(punto + h)
                derivada = (f_mas - f_x) / h
            elif formula == "atras":
                f_x = f(punto)
                f_menos = f(punto - h)
                derivada = (f_x - f_menos) / h
            else:  # central
                f_mas = f(punto + h)
                f_menos = f(punto - h)
                derivada = (f_mas - f_menos) / (2 * h)
        except (ValueError, ZeroDivisionError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="No se pudo evaluar la función en los puntos requeridos "
                        "(revisa el dominio: por ejemplo log o sqrt de negativos).",
                pasos=[],
                tabla=[],
            )

        # ---- 3. Derivada exacta y error (si es posible) ----
        try:
            derivada_exacta = float(sp.diff(expr, x).subs(x, punto))
            error_abs = abs(derivada_exacta - derivada)
            error_rel = (error_abs / abs(derivada_exacta)
                         if abs(derivada_exacta) > 1e-15 else None)
        except (TypeError, ValueError):
            derivada_exacta = None
            error_abs = None
            error_rel = None

        # ---- 4. Tabla con los puntos usados ----
        tabla = [["punto", "valor de x", "f(x)"]]
        if formula == "adelante":
            tabla.append(["x", round(punto, 8), round(f(punto), 8)])
            tabla.append(["x + h", round(punto + h, 8), round(f(punto + h), 8)])
            formula_txt = "[f(x+h) − f(x)] / h"
            orden = "O(h)"
        elif formula == "atras":
            tabla.append(["x − h", round(punto - h, 8), round(f(punto - h), 8)])
            tabla.append(["x", round(punto, 8), round(f(punto), 8)])
            formula_txt = "[f(x) − f(x−h)] / h"
            orden = "O(h)"
        else:
            tabla.append(["x − h", round(punto - h, 8), round(f(punto - h), 8)])
            tabla.append(["x + h", round(punto + h, 8), round(f(punto + h), 8)])
            formula_txt = "[f(x+h) − f(x−h)] / (2h)"
            orden = "O(h²)"

        # ---- 5. Pasos ----
        nombre_formula = {"adelante": "diferencia hacia adelante",
                          "atras": "diferencia hacia atrás",
                          "central": "diferencia central"}[formula]
        pasos = [
            f"Función: f(x) = {expr}.   Punto: x = {punto}.   Paso: h = {h}.",
            f"Fórmula elegida: {nombre_formula}, f'(x) ≈ {formula_txt}, "
            f"con error de truncamiento {orden}.",
            "Se evalúa la función en los puntos necesarios (ver tabla).",
            f"f'({punto}) ≈ {round(derivada, 8)}.",
        ]
        if derivada_exacta is not None:
            rel_txt = (f"{round(error_rel * 100, 6)} %"
                       if error_rel is not None else "n/d")
            pasos.append(
                f"Derivada exacta f'({punto}) = {round(derivada_exacta, 8)}.  "
                f"Error absoluto = {round(error_abs, 8)};  error relativo = {rel_txt}."
            )
            tabla.append(["—", "f'(x) aproximada", round(derivada, 8)])
            tabla.append(["—", "f'(x) exacta", round(derivada_exacta, 8)])
            tabla.append(["—", "error absoluto", round(error_abs, 8)])

        # ---- 6. Resultado y mensaje ----
        resultado = {"derivada_aprox": round(derivada, 8), "formula": formula}
        if derivada_exacta is not None:
            resultado["derivada_exacta"] = round(derivada_exacta, 8)
            resultado["error_abs"] = round(error_abs, 8)

        mensaje = f"f'({punto}) ≈ {round(derivada, 8)}  ({nombre_formula}, {orden})"
        if derivada_exacta is not None:
            mensaje += f"   |  exacta = {round(derivada_exacta, 6)}, error = {round(error_abs, 6)}"

        return ResultadoMetodo(
            resultado=resultado,
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )
