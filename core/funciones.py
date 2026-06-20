import sympy as sp


def crear_funcion(expresion, variable="x"):
    simbolo = sp.symbols(variable)
    funcion_simbolica = sp.sympify(expresion)
    funcion = sp.lambdify(simbolo, funcion_simbolica, "math")
    return funcion


def crear_funcion_2_variables(expresion):
    x, y = sp.symbols("x y")
    funcion_simbolica = sp.sympify(expresion)
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
