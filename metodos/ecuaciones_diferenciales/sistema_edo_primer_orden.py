import re

import sympy as sp

from core.funciones import preparar_expresion, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


def crear_funcion_3_variables(expresion):
    x, y, z = sp.symbols("x y z")
    expresion = preparar_expresion(expresion).replace("Y", "y").replace("Z", "z")
    funciones = "sin|cos|tan|log|exp|sqrt"
    for var in ("y", "z"):
        expresion = re.sub(rf"(\d)({var})", r"\1*\2", expresion)
        expresion = re.sub(rf"({var})({funciones})", r"\1*\2", expresion)
        expresion = re.sub(rf"({var})(\()", r"\1*\2", expresion)
    expresion = re.sub(r"(x|t)(y|z)", r"\1*\2", expresion)
    expresion = re.sub(r"(y)(x|t|z)", r"\1*\2", expresion)
    expresion = re.sub(r"(z)(x|t|y)", r"\1*\2", expresion)
    expr = sp.sympify(expresion, locals={
        "x": x, "t": x, "T": x, "y": y, "z": z, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "log": sp.log, "ln": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
        "pi": sp.pi, "e": sp.E,
    })
    return sp.lambdify((x, y, z), expr, "math")


class SistemaEcuacionesDiferencialesPrimerOrden(MetodoNumerico):
    nombre = "Sistema de ecuaciones diferenciales ordinarias de primer orden"
    categoria = "Ecuaciones diferenciales"
    descripcion = "Resuelve un sistema y'=f(x,y,z), z'=g(x,y,z) con Runge-Kutta de cuarto orden."

    parametros = [
        {"nombre": "funcion_y", "label": "Funcion f(x,y,z) = y'", "tipo": "text", "placeholder": "z"},
        {"nombre": "funcion_z", "label": "Funcion g(x,y,z) = z'", "tipo": "text", "placeholder": "-y"},
        {"nombre": "x0", "label": "Valor inicial x0", "tipo": "number", "placeholder": "0"},
        {"nombre": "y0", "label": "Valor inicial y0", "tipo": "number", "placeholder": "1"},
        {"nombre": "z0", "label": "Valor inicial z0", "tipo": "number", "placeholder": "0"},
        {"nombre": "h", "label": "Paso h", "tipo": "number", "placeholder": "0.1"},
        {"nombre": "n", "label": "Numero de pasos n", "tipo": "number", "placeholder": "10"},
    ]

    def ejecutar(self, **kwargs):
        f = crear_funcion_3_variables(kwargs.get("funcion_y"))
        g = crear_funcion_3_variables(kwargs.get("funcion_z"))
        x = float(kwargs.get("x0"))
        y = float(kwargs.get("y0"))
        z = float(kwargs.get("z0"))
        h = float(kwargs.get("h"))
        n = int(float(kwargs.get("n")))

        if h == 0 or n < 1:
            return ResultadoMetodo(None, "h debe ser distinto de 0 y n debe ser mayor o igual a 1.", [], [])

        tabla = []
        for i in range(1, n + 1):
            k1y = h * f(x, y, z)
            k1z = h * g(x, y, z)
            k2y = h * f(x + h / 2, y + k1y / 2, z + k1z / 2)
            k2z = h * g(x + h / 2, y + k1y / 2, z + k1z / 2)
            k3y = h * f(x + h / 2, y + k2y / 2, z + k2z / 2)
            k3z = h * g(x + h / 2, y + k2y / 2, z + k2z / 2)
            k4y = h * f(x + h, y + k3y, z + k3z)
            k4z = h * g(x + h, y + k3y, z + k3z)
            y_sig = y + (k1y + 2 * k2y + 2 * k3y + k4y) / 6
            z_sig = z + (k1z + 2 * k2z + 2 * k3z + k4z) / 6
            tabla.append({
                "i": i, "x_i": redondear(x), "y_i": redondear(y), "z_i": redondear(z),
                "k1y": redondear(k1y), "k2y": redondear(k2y), "k3y": redondear(k3y), "k4y": redondear(k4y),
                "k1z": redondear(k1z), "k2z": redondear(k2z), "k3z": redondear(k3z), "k4z": redondear(k4z),
                "y_{i+1}": redondear(y_sig), "z_{i+1}": redondear(z_sig),
            })
            x, y, z = x + h, y_sig, z_sig

        return ResultadoMetodo(
            resultado={"x": redondear(x), "y": redondear(y), "z": redondear(z)},
            mensaje=f"Aproximacion final: y({redondear(x)})={redondear(y)}, z({redondear(x)})={redondear(z)}",
            pasos=[
                "Se calculan k1, k2, k3 y k4 para cada ecuacion del sistema.",
                "Se actualizan y y z con el promedio ponderado de Runge-Kutta 4.",
            ],
            tabla=tabla,
        )
