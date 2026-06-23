import numpy as np
import sympy as sp

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_expresion


class PolinomioTaylor(MetodoNumerico):
    nombre = "Polinomio de Taylor"
    categoria = "Aproximación"
    descripcion = (
        "Construye el polinomio de Taylor de grado n de una función f(x) "
        "alrededor de un punto x0:  P(x) = Σ f⁽ᵏ⁾(x0)/k! · (x − x0)ᵏ. "
        "Además calcula el término de residuo de Lagrange "
        "R_n(x) = f⁽ⁿ⁺¹⁾(ξ)/(n+1)! · (x − x0)ⁿ⁺¹ y, al evaluar en un punto, "
        "estima una cota del error de aproximación."
    )

    parametros = [
        {"nombre": "funcion", "label": "Función f(x)",
         "tipo": "text", "placeholder": "cos(x)"},
        {"nombre": "x0", "label": "Punto de desarrollo x0",
         "tipo": "number", "placeholder": "0"},
        {"nombre": "grado", "label": "Grado n del polinomio",
         "tipo": "number", "placeholder": "4"},
        {"nombre": "x", "label": "Punto a evaluar (opcional)",
         "tipo": "number", "placeholder": "0.5"},
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

        x_eval_raw = kwargs.get("x")
        try:
            x_eval = float(x_eval_raw) if x_eval_raw not in (None, "") else None
        except (TypeError, ValueError):
            x_eval = None

        # ---- 2. Parseo simbólico ----
        try:
            x, expr = crear_expresion(funcion_txt)
        except (sp.SympifyError, SyntaxError, TypeError):
            return ResultadoMetodo(
                resultado=None,
                mensaje=f"No se pudo interpretar la función '{funcion_txt}'. "
                        "Usa sintaxis como x**2, sin(x), cos(x), exp(x), log(x).",
                pasos=[],
                tabla=[],
            )

        x0_sym = sp.nsimplify(x0) if x0 == int(x0) else sp.Float(x0)

        # ---- 3. Polinomio de Taylor término a término ----
        tabla = [["k", "f⁽ᵏ⁾(x)", "f⁽ᵏ⁾(x0)", "coef = f⁽ᵏ⁾(x0)/k!", "término"]]
        polinomio = sp.Integer(0)
        deriv = expr
        try:
            for k in range(grado + 1):
                fk_en_x0 = sp.nsimplify(deriv.subs(x, x0_sym), rational=False)
                coef = fk_en_x0 / sp.factorial(k)
                termino = coef * (x - x0_sym) ** k
                polinomio += termino
                tabla.append([
                    k,
                    str(deriv),
                    self._num(fk_en_x0),
                    self._num(coef),
                    str(sp.expand(termino)),
                ])
                deriv = sp.diff(deriv, x)  # derivada de orden k+1 para la próxima vuelta
            # tras el bucle, 'deriv' es la derivada de orden (grado+1)
            deriv_np1 = deriv
        except Exception:
            return ResultadoMetodo(
                resultado=None,
                mensaje="No se pudieron calcular las derivadas de la función "
                        "(puede no ser derivable en x0 o ser demasiado compleja).",
                pasos=[],
                tabla=[],
            )

        polinomio_simpl = sp.expand(polinomio)

        # término de residuo de Lagrange (forma simbólica)
        xi = sp.symbols("xi")
        residuo = (deriv_np1.subs(x, xi) / sp.factorial(grado + 1)
                   * (x - x0_sym) ** (grado + 1))

        # ---- 4. Pasos ----
        centro = "0 (desarrollo de Maclaurin)" if x0 == 0 else f"{self._num(x0_sym)}"
        pasos = [
            f"Función: f(x) = {expr}.",
            f"Punto de desarrollo: x0 = {centro}.  Grado: n = {grado}.",
            "Se calcula cada derivada f⁽ᵏ⁾(x), se evalúa en x0 y se obtiene el "
            "coeficiente a_k = f⁽ᵏ⁾(x0)/k! (ver tabla).",
            f"Polinomio de Taylor:  P(x) = {sp.sstr(polinomio)}",
            f"   Expandido:  P(x) = {sp.sstr(polinomio_simpl)}",
            "Término de residuo de Lagrange (ξ entre x0 y x):",
            f"   R_{grado}(x) = {sp.sstr(residuo)}",
        ]

        resultado = {"polinomio": sp.sstr(polinomio_simpl),
                     "residuo": sp.sstr(residuo)}

        # ---- 5. Evaluación y cota del error ----
        if x_eval is not None:
            try:
                p_val = float(polinomio.subs(x, x_eval))
                f_val = float(expr.subs(x, x_eval))
                err_real = abs(f_val - p_val)

                pasos.append(
                    f"Evaluando en x = {x_eval}:  P({x_eval}) = {round(p_val, 8)}, "
                    f"f({x_eval}) = {round(f_val, 8)}, error real = {round(err_real, 8)}."
                )

                # cota del error: max|f⁽ⁿ⁺¹⁾| en [x0, x] · |x-x0|^(n+1)/(n+1)!
                cota = self._cota_residuo(deriv_np1, x, x0, x_eval, grado)
                if cota is not None:
                    pasos.append(
                        f"Cota del error |R_{grado}(x)| ≤ "
                        f"max|f⁽ⁿ⁺¹⁾(ξ)|·|x−x0|ⁿ⁺¹/(n+1)! ≈ {round(cota, 8)}."
                    )
                    resultado["cota_error"] = round(cota, 8)

                tabla.append(["—", "Aproximación P(x)", "", "", round(p_val, 8)])
                tabla.append(["—", "Valor real f(x)", "", "", round(f_val, 8)])
                tabla.append(["—", "Error real", "", "", round(err_real, 8)])
                if cota is not None:
                    tabla.append(["—", "Cota del error", "", "", round(cota, 8)])

                resultado.update({"x": x_eval, "P(x)": round(p_val, 8),
                                  "f(x)": round(f_val, 8),
                                  "error_real": round(err_real, 8)})
                mensaje = (f"P(x) = {sp.sstr(polinomio_simpl)}  |  "
                           f"P({x_eval}) = {round(p_val, 6)} "
                           f"(real {round(f_val, 6)}, error {round(err_real, 6)})")
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
    #  Utilidad: cota del residuo muestreando f⁽ⁿ⁺¹⁾ en el intervalo      #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _cota_residuo(deriv_np1, x, x0, x_eval, grado):
        try:
            from math import factorial
            a, b = (x0, x_eval) if x0 <= x_eval else (x_eval, x0)
            if a == b:
                return 0.0
            f = sp.lambdify(x, deriv_np1, modules=["numpy"])
            muestras = np.linspace(a, b, 400)
            with np.errstate(all="ignore"):
                vals = np.abs(f(muestras))
            vals = vals[np.isfinite(vals)]
            if vals.size == 0:
                return None
            M = float(np.max(vals))
            return M * abs(x_eval - x0) ** (grado + 1) / factorial(grado + 1)
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    #  Utilidad: expresión sympy -> número legible cuando se pueda        #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _num(expr):
        try:
            val = float(expr)
            if abs(val - round(val)) < 1e-12:
                return int(round(val))
            return round(val, 8)
        except (TypeError, ValueError):
            return str(expr)
