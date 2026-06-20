import re
import math
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import redondear


class Newton(MetodoNumerico):
    nombre = "Newton"
    categoria = "Raíces de ecuaciones"
    descripcion = "Método de Newton-Raphson usando una aproximación inicial P0 y la derivada de la función."

    parametros = [
        {
            "nombre": "funcion",
            "label": "Función f(x)",
            "tipo": "text",
            "placeholder": "x**3 - x - 2"
        },
        {
            "nombre": "p0",
            "label": "Valor inicial P0",
            "tipo": "number",
            "placeholder": "1.5"
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

        expresion = expresion.replace("sen", "sin")
        expresion = expresion.replace("ln", "log")

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

        derivada_simbolica = sp.diff(expresion_simbolica, x)

        funcion_math = sp.lambdify(x, expresion_simbolica, "math")
        derivada_math = sp.lambdify(x, derivada_simbolica, "math")

        funcion_numpy = sp.lambdify(x, expresion_simbolica, "numpy")
        derivada_numpy = sp.lambdify(x, derivada_simbolica, "numpy")

        return (
            expresion_simbolica,
            derivada_simbolica,
            funcion_math,
            derivada_math,
            funcion_numpy,
            derivada_numpy
        )

    # =========================================================
    # UTILIDADES
    # =========================================================

    def evaluar_seguro(self, funcion, valor, nombre="función"):
        try:
            resultado = funcion(valor)
            resultado = float(resultado)
        except ZeroDivisionError:
            raise ValueError(
                f"La {nombre} no se puede evaluar en x = {valor} porque hay división entre cero."
            )
        except Exception as error:
            raise ValueError(
                f"No se pudo evaluar la {nombre} en x = {valor}. Detalle: {error}"
            )

        if not math.isfinite(resultado):
            raise ValueError(
                f"La {nombre} no tiene un valor finito en x = {valor}."
            )

        return resultado

    def signo_texto(self, valor):
        if valor > 0:
            return "(+)"
        if valor < 0:
            return "(-)"
        return "0"

    # =========================================================
    # BUSCAR INTERVALOS CON CAMBIO DE SIGNO
    # =========================================================

    def buscar_intervalos_cambio_signo(self, funcion, desde=-10, hasta=10, paso=1):
        (
            expresion_simbolica,
            derivada_simbolica,
            f,
            fp,
            f_numpy,
            fp_numpy
        ) = self.obtener_funciones(funcion)

        desde = self.convertir_numero(desde)
        hasta = self.convertir_numero(hasta)
        paso = self.convertir_numero(paso)

        if desde >= hasta:
            raise ValueError("El inicio del rango debe ser menor que el final.")

        if paso <= 0:
            raise ValueError("El paso de búsqueda debe ser mayor que cero.")

        xs = np.arange(desde, hasta + paso, paso)

        intervalos = []

        for i in range(len(xs) - 1):
            x0 = float(xs[i])
            x1 = float(xs[i + 1])

            try:
                f0 = self.evaluar_seguro(f, x0)
                f1 = self.evaluar_seguro(f, x1)
            except Exception:
                continue

            if f0 == 0:
                intervalos.append({
                    "a": x0,
                    "b": x0,
                    "fa": f0,
                    "fb": f0,
                    "p0_sugerido": x0,
                    "texto": f"[{x0:.6f}, {x0:.6f}] raíz exacta en {x0:.6f}"
                })

            elif f0 * f1 < 0:
                p0_sugerido = (x0 + x1) / 2

                intervalos.append({
                    "a": x0,
                    "b": x1,
                    "fa": f0,
                    "fb": f1,
                    "p0_sugerido": p0_sugerido,
                    "texto": f"[{x0:.6f}, {x1:.6f}] → P0 sugerido = {p0_sugerido:.6f}"
                })

        return {
            "expresion": str(expresion_simbolica),
            "derivada": str(derivada_simbolica),
            "intervalos": intervalos,
            "funcion_numpy": f_numpy,
            "derivada_numpy": fp_numpy,
        }

    # =========================================================
    # CALCULO DETALLADO
    # =========================================================

    def calcular_detallado(self, funcion, p0, tolerancia, max_iteraciones=100):
        (
            expresion_simbolica,
            derivada_simbolica,
            f,
            fp,
            f_numpy,
            fp_numpy
        ) = self.obtener_funciones(funcion)

        p_actual = self.convertir_numero(p0)
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
        raiz = p_actual
        mensaje = "Se alcanzó el máximo de iteraciones."

        for iteracion in range(1, max_iteraciones + 1):
            f_pi = self.evaluar_seguro(f, p_actual, "función")
            fp_pi = self.evaluar_seguro(fp, p_actual, "derivada")

            if abs(f_pi) <= tolerancia:
                p_siguiente = p_actual
                error = 0

                tabla.append({
                    "n": iteracion,
                    "pi": p_actual,
                    "fpi": f_pi,
                    "fppi": fp_pi,
                    "p_siguiente": p_siguiente,
                    "error": error,
                })

                raiz = p_actual
                mensaje = "Raíz aproximada encontrada dentro del error permitido."
                break

            if fp_pi == 0:
                raise ValueError(
                    f"No se puede continuar porque f'(Pᵢ) = 0 en Pᵢ = {p_actual}."
                )

            p_siguiente = p_actual - (f_pi / fp_pi)
            error = abs(p_siguiente - p_actual)

            tabla.append({
                "n": iteracion,
                "pi": p_actual,
                "fpi": f_pi,
                "fppi": fp_pi,
                "p_siguiente": p_siguiente,
                "error": error,
            })

            raiz = p_siguiente

            if error <= tolerancia:
                mensaje = "Raíz aproximada encontrada dentro del error permitido."
                break

            p_actual = p_siguiente

        return {
            "expresion": str(expresion_simbolica),
            "derivada": str(derivada_simbolica),
            "raiz": raiz,
            "mensaje": mensaje,
            "tabla": tabla,
            "funcion_numpy": f_numpy,
            "derivada_numpy": fp_numpy,
            "p0_inicial": self.convertir_numero(p0),
        }

    # =========================================================
    # EJECUCION NORMAL
    # =========================================================

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        p0 = kwargs.get("p0")
        tolerancia = kwargs.get("tolerancia")

        datos = self.calcular_detallado(
            funcion=funcion,
            p0=p0,
            tolerancia=tolerancia
        )

        tabla = []

        for fila in datos["tabla"]:
            tabla.append({
                "n": fila["n"],
                "Pᵢ": redondear(fila["pi"]),
                "f(Pᵢ)": redondear(fila["fpi"]),
                "f'(Pᵢ)": redondear(fila["fppi"]),
                "Pᵢ₊₁": redondear(fila["p_siguiente"]),
                "Error": redondear(fila["error"]),
            })

        pasos = [
            "Se obtiene automáticamente la derivada de f(x).",
            "Se evalúa f(Pᵢ) y f'(Pᵢ).",
            "Se calcula Pᵢ₊₁ = Pᵢ - f(Pᵢ)/f'(Pᵢ).",
            "Se calcula el error como |Pᵢ₊₁ - Pᵢ|.",
        ]

        return ResultadoMetodo(
            resultado=redondear(datos["raiz"]),
            mensaje=f"{datos['mensaje']} Derivada: f'(x) = {datos['derivada']}",
            pasos=pasos,
            tabla=tabla
        )