import re

import sympy as sp


def preparar_expresion(expresion):
    expresion = str(expresion).strip()
    if not expresion:
        raise ValueError("Escribe una funcion antes de calcular.")

    expresion = expresion.replace(" ", "")
    expresion = expresion.replace("^", "**")
    expresion = expresion.replace("X", "x")
    expresion = expresion.replace("sen", "sin")
    expresion = expresion.replace("ln", "log")

    funciones = "sin|cos|tan|log|exp|sqrt"
    expresion = re.sub(r"(\d)(x)", r"\1*\2", expresion)
    expresion = re.sub(r"(\d)(\()", r"\1*\2", expresion)
    expresion = re.sub(rf"(\d)({funciones})", r"\1*\2", expresion)
    expresion = re.sub(rf"(x)({funciones})", r"\1*\2", expresion)
    expresion = re.sub(r"(x)(\()", r"\1*\2", expresion)
    expresion = re.sub(r"(\))(\()", r"\1*\2", expresion)
    expresion = re.sub(rf"(\))({funciones}|x)", r"\1*\2", expresion)
    expresion = re.sub(r"(pi)(x)", r"\1*\2", expresion)
    return expresion


def crear_expresion(expresion, variable="x"):
    simbolo = sp.symbols(variable)
    locales = {
        variable: simbolo,
        variable.upper(): simbolo,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "log": sp.log,
        "ln": sp.log,
        "exp": sp.exp,
        "sqrt": sp.sqrt,
        "pi": sp.pi,
        "e": sp.E,
    }
    expresion = preparar_expresion(expresion)
    return simbolo, sp.sympify(expresion, locals=locales)


def crear_funcion(expresion, variable="x"):
    simbolo, funcion_simbolica = crear_expresion(expresion, variable)
    funcion = sp.lambdify(simbolo, funcion_simbolica, "math")
    return funcion


def crear_funcion_2_variables(expresion):
    x, y = sp.symbols("x y")
    expresion = preparar_expresion(expresion).replace("Y", "y")
    funciones = "sin|cos|tan|log|exp|sqrt"
    expresion = re.sub(r"(\d)(y)", r"\1*\2", expresion)
    expresion = re.sub(rf"(y)({funciones})", r"\1*\2", expresion)
    expresion = re.sub(r"(y)(\()", r"\1*\2", expresion)
    expresion = re.sub(r"(x)(y)", r"\1*\2", expresion)
    expresion = re.sub(r"(y)(x)", r"\1*\2", expresion)
    funcion_simbolica = sp.sympify(expresion, locals={
        "x": x, "y": y, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "log": sp.log, "ln": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
        "pi": sp.pi, "e": sp.E,
    })
    funcion = sp.lambdify((x, y), funcion_simbolica, "math")
    return funcion


def texto_a_lista_numeros(texto):
    texto = texto.replace(";", ",")
    return [float(valor.strip()) for valor in texto.split(",") if valor.strip()]


def redondear(valor, decimales=6):
    try:
        return round(float(valor), decimales)
    except Exception:
        return valor
