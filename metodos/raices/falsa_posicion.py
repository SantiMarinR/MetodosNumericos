import re
import math
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import redondear


class FalsaPosicion(MetodoNumerico):
    nombre = "Falsa posición"
    categoria = "Raíces de ecuaciones"
    descripcion = "Método que aproxima una raíz usando falsa posición dentro de un intervalo con cambio de signo."

    parametros = [
        {
            "nombre": "funcion",
            "label": "Función f(x)",
            "tipo": "text",
            "placeholder": "x**3 - x - 2"
        },
        {
            "nombre": "a",
            "label": "Valor de a",
            "tipo": "number",
            "placeholder": "1"
        },
        {
            "nombre": "b",
            "label": "Valor de b",
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

        funcion_math = sp.lambdify(x, expresion_simbolica, "math")
        funcion_numpy = sp.lambdify(x, expresion_simbolica, "numpy")

        return expresion_simbolica, funcion_math, funcion_numpy

    # =========================================================
    # UTILIDADES
    # =========================================================

    def signo_texto(self, valor):
        if valor > 0:
            return "(+)"
        if valor < 0:
            return "(-)"
        return "0"

    def calcular_max_iteraciones(self, a, b, tolerancia):
        """
        Para falsa posición usamos este número como tope automático.
        Es la misma idea de control que en bisección:
        n = ceil(log((b-a)/error) / log(2))
        """
        longitud = abs(b - a)

        if longitud <= 0:
            raise ValueError("El intervalo debe tener longitud mayor que cero.")

        if tolerancia <= 0:
            raise ValueError("El error máximo debe ser mayor que cero.")

        n = math.ceil(math.log(longitud / tolerancia) / math.log(2))

        if n <= 0:
            n = 1

        return n

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

    # =========================================================
    # CALCULO DETALLADO
    # =========================================================

    def calcular_detallado(self, funcion, a, b, tolerancia, max_iteraciones=None):
        expresion_simbolica, f, f_numpy = self.obtener_funciones(funcion)

        a = self.convertir_numero(a)
        b = self.convertir_numero(b)
        tolerancia = self.convertir_numero(tolerancia)

        if a >= b:
            raise ValueError("El valor de a debe ser menor que el valor de b.")

        if tolerancia <= 0:
            raise ValueError("El error máximo debe ser mayor que cero.")

        max_iteraciones_calculadas = self.calcular_max_iteraciones(a, b, tolerancia)

        fa = self.evaluar_seguro(f, a)
        fb = self.evaluar_seguro(f, b)

        if fa == 0:
            return {
                "expresion": str(expresion_simbolica),
                "raiz": a,
                "mensaje": "El valor de a ya es una raíz.",
                "tabla": [],
                "funcion_numpy": f_numpy,
                "a_inicial": a,
                "b_inicial": b,
                "c_final": a,
                "max_iteraciones_calculadas": max_iteraciones_calculadas,
            }

        if fb == 0:
            return {
                "expresion": str(expresion_simbolica),
                "raiz": b,
                "mensaje": "El valor de b ya es una raíz.",
                "tabla": [],
                "funcion_numpy": f_numpy,
                "a_inicial": a,
                "b_inicial": b,
                "c_final": b,
                "max_iteraciones_calculadas": max_iteraciones_calculadas,
            }

        if fa * fb > 0:
            raise ValueError(
                f"No hay cambio de signo en el intervalo. "
                f"f({a}) = {redondear(fa)} y f({b}) = {redondear(fb)}. "
                "Para aplicar falsa posición, f(a) y f(b) deben tener signos opuestos."
            )

        tabla = []
        raiz = None
        mensaje = "Se alcanzó el tope automático de iteraciones."

        a_actual = a
        b_actual = b
        c_anterior = None

        for iteracion in range(1, max_iteraciones_calculadas + 1):
            fa = self.evaluar_seguro(f, a_actual)
            fb = self.evaluar_seguro(f, b_actual)

            denominador = fb - fa

            if denominador == 0:
                raise ValueError("No se puede continuar porque f(b) - f(a) es cero.")

            # Fórmula de falsa posición:
            # c = (a f(b) - b f(a)) / (f(b) - f(a))
            c = (a_actual * fb - b_actual * fa) / denominador
            fc = self.evaluar_seguro(f, c)

            if c_anterior is None:
                error_aproximado = abs(b_actual - a_actual)
            else:
                error_aproximado = abs(c - c_anterior)

            tabla.append({
                "n": iteracion,
                "a": a_actual,
                "b": b_actual,
                "c": c,
                "fa": fa,
                "fc": fc,
                "fb": fb,
                "signo_fa": self.signo_texto(fa),
                "signo_fc": self.signo_texto(fc),
                "signo_fb": self.signo_texto(fb),
                "error": error_aproximado,
            })

            if abs(fc) <= tolerancia or (c_anterior is not None and error_aproximado <= tolerancia):
                raiz = c
                mensaje = "Raíz aproximada encontrada dentro del error permitido."
                break

            if fa * fc < 0:
                b_actual = c
            else:
                a_actual = c

            c_anterior = c

        if raiz is None:
            raiz = c

        return {
            "expresion": str(expresion_simbolica),
            "raiz": raiz,
            "mensaje": mensaje,
            "tabla": tabla,
            "funcion_numpy": f_numpy,
            "a_inicial": a,
            "b_inicial": b,
            "c_final": raiz,
            "max_iteraciones_calculadas": max_iteraciones_calculadas,
        }

    # =========================================================
    # EJECUCION NORMAL
    # =========================================================

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        a = kwargs.get("a")
        b = kwargs.get("b")
        tolerancia = kwargs.get("tolerancia")

        datos = self.calcular_detallado(
            funcion=funcion,
            a=a,
            b=b,
            tolerancia=tolerancia
        )

        tabla = []

        for fila in datos["tabla"]:
            tabla.append({
                "n": fila["n"],
                "a": redondear(fila["a"]),
                "b": redondear(fila["b"]),
                "c": redondear(fila["c"]),
                "f(a)": fila["signo_fa"],
                "f(c)": fila["signo_fc"],
                "f(b)": fila["signo_fb"],
                "Error": redondear(fila["error"]),
            })

        pasos = [
            "Se verifica que exista cambio de signo entre a y b.",
            "Se calcula c con la fórmula de falsa posición.",
            "Se revisan los signos de f(a), f(c) y f(b).",
            "Se conserva el intervalo donde existe cambio de signo.",
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