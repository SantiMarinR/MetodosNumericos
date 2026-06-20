import re
import math
import cmath
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import redondear


class Muller(MetodoNumerico):
    nombre = "Müller"
    categoria = "Raíces de ecuaciones"
    descripcion = "Método de Müller usando tres aproximaciones iniciales P0, P1 y P2."

    parametros = [
        {
            "nombre": "funcion",
            "label": "Función f(x)",
            "tipo": "text",
            "placeholder": "x**3 - x - 2"
        },
        {
            "nombre": "p0",
            "label": "P0",
            "tipo": "number",
            "placeholder": "0"
        },
        {
            "nombre": "p1",
            "label": "P1",
            "tipo": "number",
            "placeholder": "1"
        },
        {
            "nombre": "p2",
            "label": "P2",
            "tipo": "number",
            "placeholder": "2"
        },
        {
            "nombre": "tolerancia",
            "label": "Error máximo permitido",
            "tipo": "number",
            "placeholder": "1e-5"
        },
    ]

    # =========================================================
    # CONVERTIR NUMEROS
    # =========================================================

    def convertir_numero(self, texto):
        """
        Permite escribir:
        0.001
        1e-3
        1x10^-3
        1*10^-3
        1×10^-3
        """
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

    # =========================================================
    # PREPARAR FUNCION
    # =========================================================

    def preparar_expresion(self, expresion):
        expresion = str(expresion).strip()

        if not expresion:
            raise ValueError("Escribe una función antes de calcular.")

        expresion = expresion.replace(" ", "")
        expresion = expresion.replace("^", "**")

        # Permitir sen, sin, cos, tan, ln, log
        expresion = expresion.replace("sen", "sin")
        expresion = expresion.replace("ln", "log")

        # Multiplicaciones implícitas:
        # 2x -> 2*x
        # 2(x+1) -> 2*(x+1)
        # 2cos(x) -> 2*cos(x)
        # xcos(x) -> x*cos(x)
        # x(x+1) -> x*(x+1)
        # )( -> )*(
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
            raise ValueError(
                "La función no se pudo interpretar. Revisa paréntesis, multiplicaciones y operadores."
            )

        funcion_numpy = sp.lambdify(x, expresion_simbolica, "numpy")

        return expresion_simbolica, funcion_numpy

    # =========================================================
    # UTILIDADES
    # =========================================================

    def evaluar_seguro(self, funcion, valor):
        try:
            resultado = funcion(valor)
            resultado = complex(resultado)
        except ZeroDivisionError:
            raise ValueError(
                f"La función no se puede evaluar en x = {valor} porque hay división entre cero."
            )
        except Exception as error:
            raise ValueError(
                f"No se pudo evaluar la función en x = {valor}. Detalle: {error}"
            )

        if not math.isfinite(resultado.real) or not math.isfinite(resultado.imag):
            raise ValueError(
                f"La función no tiene un valor finito en x = {valor}."
            )

        return resultado

    def formatear_complejo(self, valor, decimales=10):
        valor = complex(valor)

        if abs(valor.imag) < 1e-10:
            return f"{valor.real:.{decimales}f}"

        signo = "+" if valor.imag >= 0 else "-"
        return f"{valor.real:.{decimales}f} {signo} {abs(valor.imag):.{decimales}f}i"

    def valor_para_grafica(self, valor):
        valor = complex(valor)

        if abs(valor.imag) < 1e-8:
            return float(valor.real)

        return None

    # =========================================================
    # CALCULO DETALLADO
    # =========================================================

    def calcular_detallado(self, funcion, p0, p1, p2, tolerancia, max_iteraciones=100):
        expresion_simbolica, f_numpy = self.obtener_funciones(funcion)

        p0 = complex(self.convertir_numero(p0))
        p1 = complex(self.convertir_numero(p1))
        p2 = complex(self.convertir_numero(p2))
        tolerancia = self.convertir_numero(tolerancia)

        if tolerancia <= 0:
            raise ValueError("El error máximo debe ser mayor que cero.")

        try:
            max_iteraciones = int(max_iteraciones)
        except Exception:
            max_iteraciones = 100

        if max_iteraciones <= 0:
            max_iteraciones = 100

        tabla = []
        raiz = p2
        mensaje = "Se alcanzó el máximo de iteraciones."

        for iteracion in range(1, max_iteraciones + 1):
            f0 = self.evaluar_seguro(f_numpy, p0)
            f1 = self.evaluar_seguro(f_numpy, p1)
            f2 = self.evaluar_seguro(f_numpy, p2)

            h0 = p1 - p0
            h1 = p2 - p1

            if h0 == 0 or h1 == 0:
                raise ValueError("P0, P1 y P2 deben ser valores distintos.")

            d0 = (f1 - f0) / h0
            d1 = (f2 - f1) / h1

            a = (d1 - d0) / (h1 + h0)
            b = a * h1 + d1
            c = f2

            discriminante = b ** 2 - 4 * a * c
            raiz_discriminante = cmath.sqrt(discriminante)

            denominador_1 = b + raiz_discriminante
            denominador_2 = b - raiz_discriminante

            if abs(denominador_1) > abs(denominador_2):
                denominador = denominador_1
            else:
                denominador = denominador_2

            if denominador == 0:
                raise ValueError("No se puede continuar porque el denominador se volvió cero.")

            h = (-2 * c) / denominador
            p3 = p2 + h
            error = abs(p3 - p2)

            tabla.append({
                "n": iteracion,
                "p0": p0,
                "p1": p1,
                "p2": p2,
                "f_p2": f2,
                "a": a,
                "b": b,
                "c": c,
                "p3": p3,
                "error": error,
            })

            raiz = p3

            if error <= tolerancia or abs(self.evaluar_seguro(f_numpy, p3)) <= tolerancia:
                mensaje = "Raíz aproximada encontrada dentro del error permitido."
                break

            p0 = p1
            p1 = p2
            p2 = p3

        return {
            "expresion": str(expresion_simbolica),
            "raiz": raiz,
            "raiz_texto": self.formatear_complejo(raiz),
            "mensaje": mensaje,
            "tabla": tabla,
            "funcion_numpy": f_numpy,
            "p0_inicial": tabla[0]["p0"] if tabla else p0,
            "p1_inicial": tabla[0]["p1"] if tabla else p1,
            "p2_inicial": tabla[0]["p2"] if tabla else p2,
            "c_final": raiz,
            "max_iteraciones_calculadas": max_iteraciones,
        }

    # =========================================================
    # EJECUCION NORMAL
    # =========================================================

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        p0 = kwargs.get("p0")
        p1 = kwargs.get("p1")
        p2 = kwargs.get("p2")
        tolerancia = kwargs.get("tolerancia")

        datos = self.calcular_detallado(
            funcion=funcion,
            p0=p0,
            p1=p1,
            p2=p2,
            tolerancia=tolerancia
        )

        tabla = []

        for fila in datos["tabla"]:
            tabla.append({
                "n": fila["n"],
                "P0": self.formatear_complejo(fila["p0"], 6),
                "P1": self.formatear_complejo(fila["p1"], 6),
                "P2": self.formatear_complejo(fila["p2"], 6),
                "Aprox": self.formatear_complejo(fila["p3"], 6),
                "Error": redondear(fila["error"]),
            })

        pasos = [
            "Se toman tres aproximaciones iniciales P0, P1 y P2.",
            "Se calculan h0, h1, δ0 y δ1.",
            "Se forma la parábola interpolante usando a, b y c.",
            "Se calcula P3 usando la fórmula de Müller.",
            "Se desplazan los puntos: P0=P1, P1=P2 y P2=P3.",
        ]

        return ResultadoMetodo(
            resultado=datos["raiz_texto"],
            mensaje=datos["mensaje"],
            pasos=pasos,
            tabla=tabla
        )
