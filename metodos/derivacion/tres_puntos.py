import sympy as sp
import traceback

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_expresion

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
    #  Lógica del método                                                 #
    # ------------------------------------------------------------------ #
    def ejecutar(self, **kwargs):
        try:
            # ---- Lectura de parámetros ----
            funcion_txt = str(kwargs.get("funcion", "")).strip()

            if not funcion_txt:
                return ResultadoMetodo(
                    resultado=None,
                    mensaje="Debes ingresar una función.",
                    pasos=[],
                    tabla=[]
                )

            punto = float(kwargs.get("x"))
            h = float(kwargs.get("h"))

            if h == 0:
                return ResultadoMetodo(
                    resultado=None,
                    mensaje="El valor de h no puede ser 0.",
                    pasos=[],
                    tabla=[]
                )

            formula = str(kwargs.get("formula", "central")).strip().lower()

            x = sp.symbols("x")

            # ---- Función ----
            x, expr = crear_expresion(funcion_txt)
            f = sp.lambdify(x, expr, "math")

            # ---- Fórmula seleccionada ----
            if formula == "adelante":
                desplazamientos = [0, 1, 2]
                coefs = [-3, 4, -1]
                etiquetas = ["x", "x + h", "x + 2h"]
                derivada = (
                    -3 * f(punto)
                    + 4 * f(punto + h)
                    - f(punto + 2 * h)
                ) / (2 * h)

            elif formula == "atras":
                desplazamientos = [0, -1, -2]
                coefs = [3, -4, 1]
                etiquetas = ["x", "x - h", "x - 2h"]
                derivada = (
                    3 * f(punto)
                    - 4 * f(punto - h)
                    + f(punto - 2 * h)
                ) / (2 * h)

            else:
                formula = "central"
                desplazamientos = [-1, 1]
                coefs = [-1, 1]
                etiquetas = ["x - h", "x + h"]
                derivada = (
                    f(punto + h)
                    - f(punto - h)
                ) / (2 * h)

            # ---- Derivada exacta ----
            derivada_exacta = float(
                sp.N(
                    sp.diff(expr, x).subs(x, punto)
                )
            )

            error_abs = abs(derivada_exacta - derivada)

            tabla = [["punto", "coef", "valor de x", "f(x)", "coef*f(x)"]]
            for etiqueta, coef, desplazamiento in zip(etiquetas, coefs, desplazamientos):
                xi = punto + desplazamiento * h
                fxi = f(xi)
                tabla.append([etiqueta, coef, round(xi, 8), round(fxi, 8), round(coef * fxi, 8)])
            tabla.append(["-", "", "f'(x) aproximada", round(derivada, 10), ""])
            tabla.append(["-", "", "f'(x) exacta", round(derivada_exacta, 10), ""])
            tabla.append(["-", "", "error absoluto", round(error_abs, 12), ""])

            pasos = [
                f"Función ingresada: {funcion_txt}",
                f"Punto de evaluación: x = {punto}",
                f"Paso utilizado: h = {h}",
                f"Fórmula seleccionada: {formula}",
                f"Derivada aproximada = {derivada}",
                f"Derivada exacta = {derivada_exacta}",
                f"Error absoluto = {error_abs}"
            ]

            return ResultadoMetodo(
                resultado={
                    "derivada_aprox": derivada,
                    "derivada_exacta": derivada_exacta,
                    "error_abs": error_abs
                },
                mensaje=f"f'({punto}) ≈ {round(derivada,10)}",
                pasos=pasos,
                tabla=tabla
            )

        except Exception as e:
            print(traceback.format_exc())

            return ResultadoMetodo(
                resultado=None,
                mensaje=f"ERROR: {str(e)}",
                pasos=[traceback.format_exc()],
                tabla=[]
            )
