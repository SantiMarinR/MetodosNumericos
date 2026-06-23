import re
import math
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import redondear


class DiferenciaDivididaAdelante(MetodoNumerico):
    nombre = "Diferencia dividida adelante"
    categoria = "Interpolación"
    descripcion = "Interpolación por diferencias divididas de Newton hacia adelante."

    parametros = []

    def convertir_numero(self, texto):
        texto = str(texto).strip().lower()
        texto = texto.replace(" ", "")
        texto = texto.replace(",", ".")
        texto = texto.replace("×", "x")

        if texto == "":
            raise ValueError("Falta ingresar un valor numérico.")

        patron_x = r"^([+-]?\d+(\.\d+)?)x10\^([+-]?\d+)$"
        coincidencia = re.match(patron_x, texto)
        if coincidencia:
            base = float(coincidencia.group(1))
            exponente = int(coincidencia.group(3))
            return base * (10 ** exponente)

        patron_asterisco = r"^([+-]?\d+(\.\d+)?)\*10\^([+-]?\d+)$"
        coincidencia = re.match(patron_asterisco, texto)
        if coincidencia:
            base = float(coincidencia.group(1))
            exponente = int(coincidencia.group(3))
            return base * (10 ** exponente)

        return float(texto)

    def preparar_expresion(self, expresion):
        expresion = str(expresion).strip()
        if not expresion:
            raise ValueError("Escribe una función antes de calcular.")

        expresion = expresion.replace(" ", "")
        expresion = expresion.replace("^", "**")
        expresion = expresion.replace("sen", "sin")
        expresion = expresion.replace("ln", "log")
        expresion = expresion.replace("e(", "exp(")

        expresion = re.sub(r"(\d)(x)", r"\1*\2", expresion)
        expresion = re.sub(r"(\d)(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(\d)(sin|cos|tan|log|exp|sqrt)", r"\1*\2", expresion)
        expresion = re.sub(r"(x)(sin|cos|tan|log|exp|sqrt)", r"\1*\2", expresion)
        expresion = re.sub(r"(x)(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(\))(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(\))(sin|cos|tan|log|exp|sqrt|x)", r"\1*\2", expresion)
        return expresion

    def obtener_funciones(self, expresion):
        x = sp.symbols("x")
        expresion = self.preparar_expresion(expresion)
        locales = {
            "x": x,
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
        try:
            expresion_simbolica = sp.sympify(expresion, locals=locales)
        except Exception:
            raise ValueError("La función no se pudo interpretar. Revisa paréntesis, multiplicaciones y operadores.")

        funcion_math = sp.lambdify(x, expresion_simbolica, "math")
        funcion_numpy = sp.lambdify(x, expresion_simbolica, "numpy")
        return x, expresion_simbolica, funcion_math, funcion_numpy

    def evaluar_seguro(self, funcion, valor):
        try:
            resultado = float(funcion(valor))
        except ZeroDivisionError:
            raise ValueError(f"La función no se puede evaluar en x = {valor} porque hay división entre cero.")
        except Exception as error:
            raise ValueError(f"No se pudo evaluar la función en x = {valor}. Detalle: {error}")

        if not math.isfinite(resultado):
            raise ValueError(f"La función no tiene un valor finito en x = {valor}.")
        return resultado

    def construir_tabla_diferencias(self, xs, ys):
        n = len(xs)
        tabla = [[None for _ in range(n)] for _ in range(n)]

        for i in range(n):
            tabla[i][0] = float(ys[i])

        for orden in range(1, n):
            for i in range(n - orden):
                denominador = xs[i + orden] - xs[i]
                if denominador == 0:
                    raise ValueError("No se permiten valores x repetidos.")
                tabla[i][orden] = (tabla[i + 1][orden - 1] - tabla[i][orden - 1]) / denominador

        return tabla

    def formato_numero(self, valor, decimales=8):
        try:
            return f"{float(valor):.{decimales}f}".rstrip("0").rstrip(".")
        except Exception:
            return str(valor)

    def construir_newton(self, x_symbol, xs_ordenados, coeficientes):
        polinomio = 0
        terminos = []

        for k, coef in enumerate(coeficientes):
            producto = 1
            factores_texto = []

            for j in range(k):
                producto *= (x_symbol - xs_ordenados[j])
                factores_texto.append(f"(x - {self.formato_numero(xs_ordenados[j], 6)})")

            termino = coef * producto
            polinomio += termino

            if k == 0:
                terminos.append(f"{self.formato_numero(coef, 8)}")
            else:
                terminos.append(f"{self.formato_numero(coef, 8)}" + "".join(factores_texto))

        texto_newton = "P(x) = " + " + ".join(terminos)
        texto_newton = texto_newton.replace("+ -", "- ")
        return sp.expand(polinomio), texto_newton

    def calcular_detallado(self, funcion=None, puntos_x=None, puntos_y=None, modo="Adelante"):
        x_symbol = sp.symbols("x")
        xs_originales = [self.convertir_numero(valor) for valor in puntos_x]

        if len(xs_originales) < 2:
            raise ValueError("Necesitas al menos 2 puntos para interpolar.")

        if len(set(xs_originales)) != len(xs_originales):
            raise ValueError("No se permiten valores x repetidos.")

        if puntos_y is None:
            x_symbol, funcion_simbolica, f_math, f_numpy = self.obtener_funciones(funcion)
            ys_originales = [self.evaluar_seguro(f_math, xi) for xi in xs_originales]
            expresion_texto = str(funcion_simbolica)
        else:
            ys_originales = [self.convertir_numero(valor) for valor in puntos_y]
            if len(ys_originales) != len(xs_originales):
                raise ValueError("La cantidad de valores y debe coincidir con la cantidad de valores x.")
            f_numpy = None
            expresion_texto = "Datos capturados manualmente"

        modo_normalizado = str(modo).strip().lower()

        if "atr" in modo_normalizado:
            modo_usado = "Atrás"
            xs_ordenados = list(reversed(xs_originales))
            ys_ordenados = list(reversed(ys_originales))
        else:
            modo_usado = "Adelante"
            xs_ordenados = xs_originales[:]
            ys_ordenados = ys_originales[:]

        tabla = self.construir_tabla_diferencias(xs_ordenados, ys_ordenados)
        coeficientes = [tabla[0][orden] for orden in range(len(xs_ordenados))]

        polinomio_expandido, polinomio_newton_texto = self.construir_newton(
            x_symbol=x_symbol,
            xs_ordenados=xs_ordenados,
            coeficientes=coeficientes,
        )

        polinomio_numpy = sp.lambdify(x_symbol, polinomio_expandido, "numpy")

        encabezados = ["i", "xᵢ", "f(xᵢ)"]
        for orden in range(1, len(xs_ordenados)):
            encabezados.append(f"Dif. orden {orden}")

        tabla_visible = []
        for i in range(len(xs_ordenados)):
            fila = [i, xs_ordenados[i], ys_ordenados[i]]
            for orden in range(1, len(xs_ordenados)):
                fila.append(tabla[i][orden] if i <= len(xs_ordenados) - orden - 1 else None)
            tabla_visible.append(fila)

        return {
            "modo": modo_usado,
            "expresion": expresion_texto,
            "usa_funcion": f_numpy is not None,
            "puntos_x_originales": xs_originales,
            "puntos_y_originales": ys_originales,
            "puntos_x": xs_ordenados,
            "puntos_y": ys_ordenados,
            "tabla": tabla,
            "tabla_visible": tabla_visible,
            "encabezados": encabezados,
            "coeficientes": coeficientes,
            "polinomio_newton": polinomio_newton_texto,
            "polinomio_expandido": str(sp.N(polinomio_expandido, 12)),
            "polinomio_expandido_exacto": str(sp.expand(polinomio_expandido)),
            "funcion_numpy": f_numpy,
            "polinomio_numpy": polinomio_numpy,
            "resultado": polinomio_expandido,
        }

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        puntos_x = kwargs.get("puntos_x", [])
        puntos_y = kwargs.get("puntos_y")
        modo = kwargs.get("modo", "Adelante")

        datos = self.calcular_detallado(funcion=funcion, puntos_x=puntos_x, puntos_y=puntos_y, modo=modo)

        tabla = []
        for fila in datos["tabla_visible"]:
            registro = {}
            for encabezado, valor in zip(datos["encabezados"], fila):
                registro[encabezado] = "" if valor is None else redondear(valor)
            tabla.append(registro)

        return ResultadoMetodo(
            resultado=datos["polinomio_expandido"],
            mensaje=f"Polinomio interpolante calculado por diferencias divididas hacia {datos['modo'].lower()}.",
            pasos=[
                "Se evalúan los valores yᵢ = f(xᵢ).",
                "Se construye la tabla triangular de diferencias divididas.",
                "Se toman los coeficientes de Newton según el modo seleccionado.",
                "Se forma el polinomio interpolante.",
            ],
            tabla=tabla,
        )
