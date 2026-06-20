import re
import math
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import redondear


class Neville(MetodoNumerico):
    nombre = "Neville"
    categoria = "Interpolación"
    descripcion = "Interpolación de Neville construyendo el polinomio interpolante a partir de puntos xᵢ."

    parametros = [
        {
            "nombre": "funcion",
            "label": "Función f(x)",
            "tipo": "text",
            "placeholder": "3*x**2*sin(x)"
        },
        {
            "nombre": "puntos_x",
            "label": "Valores de xᵢ separados por coma",
            "tipo": "text",
            "placeholder": "1, 1.4, 1.8, 2.2"
        },
    ]

    # =========================================================
    # CONVERSIONES
    # =========================================================

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

        # Permite escribir e(2*x-8) como exp(2*x-8)
        expresion = expresion.replace("e(", "exp(")

        # Multiplicaciones implícitas comunes
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
        expresion_preparada = self.preparar_expresion(expresion)

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
            funcion_simbolica = sp.sympify(expresion_preparada, locals=locales)
        except Exception:
            raise ValueError(
                "La función no se pudo interpretar. Revisa paréntesis, multiplicaciones y operadores."
            )

        funcion_math = sp.lambdify(x, funcion_simbolica, "math")
        funcion_numpy = sp.lambdify(x, funcion_simbolica, "numpy")

        return x, funcion_simbolica, funcion_math, funcion_numpy

    def evaluar_seguro(self, funcion, valor):
        try:
            resultado = funcion(valor)
            resultado = float(resultado)
        except ZeroDivisionError:
            raise ValueError(
                f"La función no se puede evaluar en x = {valor} porque hay división entre cero."
            )
        except Exception as error:
            raise ValueError(
                f"No se pudo evaluar la función en x = {valor}. Detalle: {error}"
            )

        if not math.isfinite(resultado):
            raise ValueError(f"La función no tiene un valor finito en x = {valor}.")

        return resultado

    def obtener_puntos_desde_texto(self, puntos_x):
        if isinstance(puntos_x, (list, tuple)):
            xs = [self.convertir_numero(valor) for valor in puntos_x]
        else:
            texto = str(puntos_x).strip()
            if not texto:
                raise ValueError("Escribe los valores de xᵢ.")

            partes = texto.replace(";", ",").split(",")
            xs = [self.convertir_numero(parte) for parte in partes if str(parte).strip() != ""]

        if len(xs) < 2:
            raise ValueError("Neville necesita al menos 2 puntos.")

        if len(xs) != len(set(xs)):
            raise ValueError("Los valores xᵢ no pueden repetirse.")

        return xs

    def texto_numero(self, valor, decimales=6):
        try:
            return f"{float(valor):.{decimales}f}"
        except Exception:
            return str(valor)

    def texto_polinomio(self, expresion, digitos=10):
        try:
            return sp.sstr(sp.N(sp.expand(expresion), digitos)).replace("**", "^")
        except Exception:
            return str(expresion).replace("**", "^")

    def nombre_p(self, i, j):
        if j == 0:
            return f"P{i}"
        indices = ",".join(str(valor) for valor in range(i, i + j + 1))
        return f"P{indices}"

    # =========================================================
    # TABLA DE NEVILLE COMO POLINOMIOS Pᵢ
    # =========================================================

    def construir_tabla_neville_polinomios(self, variable, puntos_x, puntos_y):
        n = len(puntos_x)
        q = [[None for _ in range(n)] for _ in range(n)]

        for i in range(n):
            q[i][0] = sp.Float(puntos_y[i])

        for j in range(1, n):
            for i in range(0, n - j):
                xi = sp.Float(puntos_x[i])
                xij = sp.Float(puntos_x[i + j])
                denominador = xi - xij

                if denominador == 0:
                    raise ValueError("No se puede continuar porque hay valores xᵢ repetidos.")

                q[i][j] = sp.expand(
                    ((variable - xij) * q[i][j - 1]
                     - (variable - xi) * q[i + 1][j - 1])
                    / denominador
                )

        return q

    def calcular_detallado(self, funcion, puntos_x):
        variable, funcion_simbolica, funcion_math, funcion_numpy = self.obtener_funciones(funcion)
        puntos_x = self.obtener_puntos_desde_texto(puntos_x)
        puntos_y = [self.evaluar_seguro(funcion_math, xi) for xi in puntos_x]

        tabla_neville = self.construir_tabla_neville_polinomios(
            variable,
            puntos_x,
            puntos_y,
        )

        polinomio = sp.expand(tabla_neville[0][len(puntos_x) - 1])
        polinomio_numpy = sp.lambdify(variable, polinomio, "numpy")

        tabla = []
        n = len(puntos_x)
        for i in range(n):
            fila = {
                "i": i,
                "xi": puntos_x[i],
                "yi": puntos_y[i],
                "valores_q": [],
                "valores_q_texto": [],
            }
            for j in range(n):
                valor = tabla_neville[i][j]
                fila["valores_q"].append(valor)
                fila["valores_q_texto"].append("" if valor is None else self.texto_polinomio(valor, 8))
            tabla.append(fila)

        pasos = [
            "Se calculan los valores yᵢ = f(xᵢ).",
            "La primera columna de Neville es Pᵢ(x) = f(xᵢ).",
            "Se llena la tabla triangular usando la fórmula recursiva de Neville.",
            "El polinomio final es P0,1,2,...,n(x).",
        ]

        return {
            "funcion_texto": str(funcion),
            "funcion_simbolica": funcion_simbolica,
            "funcion_numpy": funcion_numpy,
            "puntos_x": puntos_x,
            "puntos_y": puntos_y,
            "tabla_neville": tabla_neville,
            "tabla": tabla,
            "polinomio": polinomio,
            "polinomio_texto": self.texto_polinomio(polinomio, 10),
            "polinomio_numpy": polinomio_numpy,
            "pasos": pasos,
            "mensaje": "Polinomio interpolante de Neville calculado correctamente.",
        }

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        puntos_x = kwargs.get("puntos_x")
        datos = self.calcular_detallado(funcion, puntos_x)

        tabla_salida = []
        for fila in datos["tabla"]:
            fila_salida = {
                "i": fila["i"],
                "xᵢ": redondear(fila["xi"]),
                "Pᵢ=f(xᵢ)": redondear(fila["yi"]),
            }
            for j, valor in enumerate(fila["valores_q"][1:], start=1):
                fila_salida[self.nombre_p(fila["i"], j) + "(x)"] = "" if valor is None else fila["valores_q_texto"][j]
            tabla_salida.append(fila_salida)

        return ResultadoMetodo(
            resultado=datos["polinomio_texto"],
            mensaje=f"{datos['mensaje']} P(x) = P0,{len(datos['puntos_x']) - 1}(x) = {datos['polinomio_texto']}",
            pasos=datos["pasos"],
            tabla=tabla_salida,
        )
