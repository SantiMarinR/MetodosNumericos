import math

import sympy as sp

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class DesarrolloPolinomios(MetodoNumerico):
    nombre = "Desarrollo en polinomios"
    categoria = "Aproximación"
    descripcion = (
        "Aproxima una función f(x) mediante su polinomio de Taylor alrededor de "
        "un punto x0, hasta un grado n dado: "
        "P(x) = Σ f⁽ᵏ⁾(x0)/k! · (x − x0)ᵏ. Si x0 = 0 se obtiene el desarrollo de "
        "Maclaurin. Opcionalmente evalúa el polinomio en un punto y lo compara "
        "con el valor real de la función."
    )

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)",
         "tipo": "text", "placeholder": "exp(x)"},
        {"nombre": "x0", "label": "Punto de desarrollo x0",
         "tipo": "number", "placeholder": "0"},
        {"nombre": "grado", "label": "Grado del polinomio",
         "tipo": "number", "placeholder": "4"},
        {"nombre": "x", "label": "Punto a evaluar (opcional)",
         "tipo": "number", "placeholder": "1"},
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
            x0_raw = kwargs.get("x0")
            x0 = float(x0_raw) if x0_raw not in (None, "") else 0.0
            grado_raw = kwargs.get("grado")
            grado = int(float(grado_raw)) if grado_raw not in (None, "") else 4
        except (TypeError, ValueError):
            return ResultadoMetodo(
                resultado=None,
                mensaje="x0 debe ser un número y el grado un entero.",
                pasos=[],
                tabla=[],
            )

        if grado < 0:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El grado debe ser un entero mayor o igual a 0.",
                pasos=[],
                tabla=[],
            )

        # punto de evaluación opcional
        x_eval_raw = kwargs.get("x")
        try:
            x_eval = float(x_eval_raw) if x_eval_raw not in (None, "") else None
        except (TypeError, ValueError):
            x_eval = None

        # ---- 2. Parseo simbólico de la función ----
        x = sp.symbols("x")
        try:
            expr = sp.sympify(str(funcion_txt).replace("^", "**"))
        except (sp.SympifyError, SyntaxError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje=f"No se pudo interpretar la función '{funcion_txt}'. "
                        "Usa sintaxis como x**2, sin(x), exp(x), log(x).",
                pasos=[],
                tabla=[],
            )

        x0_sym = sp.nsimplify(x0) if x0 == int(x0) else sp.Float(x0)

        # ---- 3. Construcción del polinomio de Taylor término a término ----
        tabla = [["k", "f⁽ᵏ⁾(x)", "f⁽ᵏ⁾(x0)", "coef = f⁽ᵏ⁾(x0)/k!", "término"]]
        terminos = []
        polinomio = sp.Integer(0)
        deriv = expr
        try:
            for k in range(grado + 1):
                # k-ésima derivada (deriv ya es la derivada de orden k)
                fk_en_x0 = deriv.subs(x, x0_sym)
                fk_en_x0 = sp.nsimplify(fk_en_x0, rational=False)
                coef = fk_en_x0 / sp.factorial(k)
                termino = coef * (x - x0_sym) ** k
                polinomio += termino
                terminos.append(termino)

                tabla.append([
                    k,
                    str(deriv),
                    self._num(fk_en_x0),
                    self._num(coef),
                    str(sp.expand(termino)),
                ])

                # preparar la derivada del siguiente orden
                deriv = sp.diff(deriv, x)
        except Exception:
            return ResultadoMetodo(
                resultado=None,
                mensaje="No se pudieron calcular las derivadas de la función "
                        "(puede no ser derivable en x0 o ser demasiado compleja).",
                pasos=[],
                tabla=[],
            )

        polinomio_simpl = sp.expand(polinomio)

        # ---- 4. Pasos explicativos ----
        centro = "0 (desarrollo de Maclaurin)" if x0 == 0 else f"{self._num(x0_sym)}"
        pasos = [
            f"Función: f(x) = {expr}.",
            f"Punto de desarrollo: x0 = {centro}.  Grado: {grado}.",
            "Se calcula cada derivada f⁽ᵏ⁾(x), se evalúa en x0 y se obtiene el "
            "coeficiente a_k = f⁽ᵏ⁾(x0)/k! (ver tabla).",
            "El polinomio de Taylor es la suma de los términos a_k·(x − x0)ᵏ:",
            f"   P(x) = {sp.sstr(polinomio)}",
            f"   Expandido: P(x) = {sp.sstr(polinomio_simpl)}",
        ]

        resultado = {"polinomio": sp.sstr(polinomio_simpl)}

        # ---- 5. Evaluación opcional y comparación con el valor real ----
        if x_eval is not None:
            try:
                p_val = float(polinomio.subs(x, x_eval))
                f_val = float(expr.subs(x, x_eval))
                err_abs = abs(f_val - p_val)
                err_rel = (err_abs / abs(f_val)) if abs(f_val) > 1e-15 else None

                pasos.append(
                    f"Evaluando en x = {x_eval}:  P({x_eval}) = {round(p_val, 8)}  "
                    f"y el valor real f({x_eval}) = {round(f_val, 8)}."
                )
                rel_txt = (f"{round(err_rel * 100, 6)} %"
                           if err_rel is not None else "n/d")
                pasos.append(
                    f"Error absoluto = {round(err_abs, 8)};  error relativo = {rel_txt}."
                )

                tabla.append(["—", "Aproximación P(x)", "", "", round(p_val, 8)])
                tabla.append(["—", "Valor real f(x)", "", "", round(f_val, 8)])
                tabla.append(["—", "Error absoluto", "", "", round(err_abs, 8)])

                resultado.update({
                    "x": x_eval,
                    "P(x)": round(p_val, 8),
                    "f(x)": round(f_val, 8),
                    "error_abs": round(err_abs, 8),
                })
                mensaje = (f"P(x) = {sp.sstr(polinomio_simpl)}   |   "
                           f"P({x_eval}) = {round(p_val, 6)} "
                           f"(real {round(f_val, 6)}, error {round(err_abs, 6)})")
            except (TypeError, ValueError):
                mensaje = f"Polinomio de Taylor de grado {grado}:  P(x) = {sp.sstr(polinomio_simpl)}"
        else:
            mensaje = f"Polinomio de Taylor de grado {grado}:  P(x) = {sp.sstr(polinomio_simpl)}"

        return ResultadoMetodo(
            resultado=resultado,
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )

    # ------------------------------------------------------------------ #
    #  Utilidad: pasa una expresión sympy a número legible cuando se pueda #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _num(expr):
        try:
            val = float(expr)
            # entero limpio -> sin decimales
            if abs(val - round(val)) < 1e-12:
                return int(round(val))
            return round(val, 8)
        except (TypeError, ValueError):
            return str(expr)