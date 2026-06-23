import math
import re

import sympy as sp

from core.funciones import preparar_expresion, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class TaylorOrdenN(MetodoNumerico):
    nombre = "Taylor de orden n"
    categoria = "Ecuaciones diferenciales"
    descripcion = "Resuelve y'=f(x,y) usando el metodo de Taylor de orden n."

    parametros = [
        {"nombre": "funcion", "label": "Funcion f(x,y) = y'", "tipo": "text", "placeholder": "x + y"},
        {"nombre": "x0", "label": "Valor inicial x0", "tipo": "number", "placeholder": "0"},
        {"nombre": "y0", "label": "Valor inicial y0", "tipo": "number", "placeholder": "1"},
        {"nombre": "h", "label": "Paso h", "tipo": "number", "placeholder": "0.1"},
        {"nombre": "n", "label": "Numero de pasos", "tipo": "number", "placeholder": "10"},
        {"nombre": "orden", "label": "Orden de Taylor", "tipo": "number", "placeholder": "4"},
    ]

    def _expresion_dos_variables(self, texto):
        x, y = sp.symbols("x y")
        expresion = preparar_expresion(texto).replace("Y", "y")
        funciones = "sin|cos|tan|log|exp|sqrt"
        expresion = re.sub(r"(\d)(y)", r"\1*\2", expresion)
        expresion = re.sub(rf"(y)({funciones})", r"\1*\2", expresion)
        expresion = re.sub(r"(y)(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(x|t)(y)", r"\1*\2", expresion)
        expresion = re.sub(r"(y)(x|t)", r"\1*\2", expresion)
        expr = sp.sympify(expresion, locals={
            "x": x, "t": x, "T": x, "y": y, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "log": sp.log, "ln": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
            "pi": sp.pi, "e": sp.E,
        })
        return x, y, expr

    def ejecutar(self, **kwargs):
        x, y, f_expr = self._expresion_dos_variables(kwargs.get("funcion"))
        x_val = float(kwargs.get("x0"))
        y_val = float(kwargs.get("y0"))
        h = float(kwargs.get("h"))
        pasos_n = int(float(kwargs.get("n")))
        orden = int(float(kwargs.get("orden")))

        if h == 0 or pasos_n < 1 or orden < 1:
            return ResultadoMetodo(None, "h debe ser distinto de 0, pasos >= 1 y orden >= 1.", [], [])

        derivadas = [None, f_expr]
        actual = f_expr
        for _ in range(2, orden + 1):
            actual = sp.diff(actual, x) + sp.diff(actual, y) * f_expr
            derivadas.append(sp.simplify(actual))

        funciones = [None] + [sp.lambdify((x, y), derivadas[k], "math") for k in range(1, orden + 1)]

        tabla = []
        pasos = [
            "Se calculan derivadas totales usando y'=f(x,y).",
            "Formula: y_{i+1}=y_i + h*y' + h^2/2!*y'' + ... + h^n/n!*y^(n).",
            "Cada termino se evalua en (x_i, y_i).",
        ]
        for i in range(1, pasos_n + 1):
            incremento = 0.0
            fila = {"i": i, "x_i": redondear(x_val), "y_i": redondear(y_val)}
            terminos_texto = []
            for k in range(1, orden + 1):
                valor_derivada = float(funciones[k](x_val, y_val))
                termino = (h ** k / math.factorial(k)) * valor_derivada
                incremento += termino
                fila[f"y^{k}"] = redondear(valor_derivada)
                fila[f"term {k}"] = redondear(termino)
                terminos_texto.append(
                    f"h^{k}/{k}!*y^{k} = {redondear(termino)}"
                )
            y_sig = y_val + incremento
            fila["y_{i+1}"] = redondear(y_sig)
            tabla.append(fila)
            if i <= 20:
                pasos.extend([
                    f"Iteracion {i}: x_i={redondear(x_val)}, y_i={redondear(y_val)}.",
                    "Terminos: " + "; ".join(terminos_texto) + ".",
                    f"Incremento = {redondear(incremento)}; y_{i + 1} = {redondear(y_val)} + {redondear(incremento)} = {redondear(y_sig)}.",
                ])
            x_val, y_val = x_val + h, y_sig

        if pasos_n > 20:
            pasos.append("Se omiten del procedimiento escrito las iteraciones restantes para no saturar la pantalla; la tabla conserva todos los valores.")

        return ResultadoMetodo(
            resultado={"x": redondear(x_val), "y": redondear(y_val)},
            mensaje=f"Aproximacion final por Taylor orden {orden}: y({redondear(x_val)}) = {redondear(y_val)}",
            pasos=pasos,
            tabla=tabla,
        )
