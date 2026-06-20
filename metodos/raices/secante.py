import re
import math
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import redondear


class Secante(MetodoNumerico):
    nombre = "Secante"
    categoria = "Raíces de ecuaciones"
    descripcion = "Método que aproxima una raíz usando dos aproximaciones iniciales p0 y p1."

    parametros = [
        {
            "nombre": "funcion",
            "label": "Función f(x)",
            "tipo": "text",
            "placeholder": "x**3 - x - 2"
        },
        {
            "nombre": "p0",
            "label": "Valor de p0",
            "tipo": "number",
            "placeholder": "0"
        },
        {
            "nombre": "p1",
            "label": "Valor de p1 / p0+1",
            "tipo": "number",
            "placeholder": "2"
        },
        {
            "nombre": "tolerancia",
            "label": "Error máximo permitido",
            "tipo": "number",
            "placeholder": "0.001"
        },
    ]

    # =========================================================
    # CONVERSION DE NUMEROS
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

        funcion_math = sp.lambdify(x, expresion_simbolica, "math")
        funcion_numpy = sp.lambdify(x, expresion_simbolica, "numpy")

        return expresion_simbolica, funcion_math, funcion_numpy

    # =========================================================
    # UTILIDADES
    # =========================================================

    def evaluar_seguro(self, funcion, valor):
        try:
            resultado = funcion(valor)
            resultado = float(resultado)
        except ZeroDivisionError:
            raise ValueError(
                f"La función no se puede evaluar en x = {valor} porque hay división entre cero."
            )
        except ValueError:
            raise ValueError(
                f"La función no se puede evaluar en x = {valor}. Revisa el dominio."
            )
        except Exception as error:
            raise ValueError(
                f"No se pudo evaluar la función en x = {valor}. Detalle: {error}"
            )

        if not math.isfinite(resultado):
            raise ValueError(
                f"La función no tiene un valor finito en x = {valor}."
            )

        return resultado

    def signo_texto(self, valor):
        if valor > 0:
            return "(+)"
        if valor < 0:
            return "(-)"
        return "0"

    # =========================================================
    # CALCULO DETALLADO
    # =========================================================

    def calcular_detallado(self, funcion, p0, p1, tolerancia, max_iteraciones=None):
        expresion_simbolica, f, f_numpy = self.obtener_funciones(funcion)

        p0 = self.convertir_numero(p0)
        p1 = self.convertir_numero(p1)
        tolerancia = self.convertir_numero(tolerancia)

        if tolerancia <= 0:
            raise ValueError("El error máximo debe ser mayor que cero.")

        if p0 == p1:
            raise ValueError("p0 y p1 deben ser diferentes.")

        # En secante no hay una fórmula universal segura para el número mínimo.
        # Usamos 100 como tope automático para evitar ciclos infinitos.
        if max_iteraciones is None:
            max_iteraciones_calculadas = 100
        else:
            try:
                max_iteraciones_calculadas = int(max_iteraciones)
            except Exception:
                max_iteraciones_calculadas = 100

            if max_iteraciones_calculadas <= 0:
                max_iteraciones_calculadas = 100

        tabla = []
        mensaje = "Se alcanzó el tope automático de iteraciones."
        raiz = None

        pi = p0
        pi_mas_1 = p1

        for iteracion in range(max_iteraciones_calculadas):
            f_pi = self.evaluar_seguro(f, pi)
            f_pi_mas_1 = self.evaluar_seguro(f, pi_mas_1)

            denominador = f_pi_mas_1 - f_pi

            if denominador == 0:
                raise ValueError("No se puede continuar porque f(pᵢ₊₁) - f(pᵢ) es cero.")

            # Fórmula de secante:
            # p_{i+2} = p_{i+1} - f(p_{i+1}) * (p_{i+1}-p_i) / (f(p_{i+1})-f(p_i))
            p_aprox = pi_mas_1 - (f_pi_mas_1 * (pi_mas_1 - pi)) / denominador
            f_aprox = self.evaluar_seguro(f, p_aprox)
            error = abs(p_aprox - pi_mas_1)

            tabla.append({
                "n": iteracion,
                "pi": pi,
                "pi_mas_1": pi_mas_1,
                "aprox": p_aprox,
                "f_pi": f_pi,
                "f_pi_mas_1": f_pi_mas_1,
                "f_aprox": f_aprox,
                "signo_fpi": self.signo_texto(f_pi),
                "signo_fpi_mas_1": self.signo_texto(f_pi_mas_1),
                "signo_aprox": self.signo_texto(f_aprox),
                "error": error,
            })

            if abs(f_aprox) <= tolerancia or error <= tolerancia:
                raiz = p_aprox
                mensaje = "Raíz aproximada encontrada dentro del error permitido."
                break

            pi = pi_mas_1
            pi_mas_1 = p_aprox

        if raiz is None:
            raiz = p_aprox

        return {
            "expresion": str(expresion_simbolica),
            "raiz": raiz,
            "mensaje": mensaje,
            "tabla": tabla,
            "funcion_numpy": f_numpy,
            "p0_inicial": p0,
            "p1_inicial": p1,
            "c_final": raiz,
            "max_iteraciones_calculadas": max_iteraciones_calculadas,
        }

    # =========================================================
    # EJECUCION NORMAL
    # =========================================================

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        p0 = kwargs.get("p0")
        p1 = kwargs.get("p1")
        tolerancia = kwargs.get("tolerancia")

        datos = self.calcular_detallado(
            funcion=funcion,
            p0=p0,
            p1=p1,
            tolerancia=tolerancia
        )

        tabla = []

        for fila in datos["tabla"]:
            tabla.append({
                "Iteración": fila["n"],
                "Pᵢ": redondear(fila["pi"]),
                "Pᵢ₊₁": redondear(fila["pi_mas_1"]),
                "Aprox": redondear(fila["aprox"]),
                "Error": redondear(fila["error"]),
            })

        pasos = [
            "Se toman dos aproximaciones iniciales p0 y p1.",
            "Se calcula una recta secante entre los puntos de la función.",
            "Se obtiene la nueva aproximación con la fórmula de la secante.",
            "Se repite el proceso usando pᵢ = pᵢ₊₁ y pᵢ₊₁ = aproximación nueva.",
        ]

        return ResultadoMetodo(
            resultado=redondear(datos["raiz"]),
            mensaje=(
                f"{datos['mensaje']} "
                f"Tope automático de iteraciones: {datos['max_iteraciones_calculadas']}."
            ),
            pasos=pasos,
            tabla=tabla
        )
