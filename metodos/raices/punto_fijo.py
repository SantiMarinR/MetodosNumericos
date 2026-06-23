import math
import re

import numpy as np
import sympy as sp

from core.funciones import crear_expresion, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class PuntoFijo(MetodoNumerico):
    nombre = "Punto fijo"
    categoria = "Raices de ecuaciones"
    descripcion = (
        "Aproxima un punto fijo de g(x), usando la iteracion p_i = g(p_{i-1}). "
        "Si f(x)=0 se despeja primero como x=g(x)."
    )

    parametros = [
        {"nombre": "funcion", "label": "Funcion g(x)", "tipo": "text", "placeholder": "cos(x)"},
        {"nombre": "p0", "label": "Valor inicial P0", "tipo": "number", "placeholder": "0.5"},
        {"nombre": "tolerancia", "label": "Error maximo permitido", "tipo": "number", "placeholder": "1e-5"},
        {"nombre": "max_iteraciones", "label": "Maximo de iteraciones (opcional)", "tipo": "number", "placeholder": "Se calcula automaticamente"},
    ]

    def convertir_numero(self, texto):
        texto = str(texto).strip().lower().replace(" ", "").replace(",", ".").replace("×", "x")
        if texto == "":
            raise ValueError("Falta ingresar un valor numerico.")

        for patron in (r"^([+-]?\d+(\.\d+)?)x10\^([+-]?\d+)$",
                       r"^([+-]?\d+(\.\d+)?)\*10\^([+-]?\d+)$"):
            coincidencia = re.match(patron, texto)
            if coincidencia:
                return float(coincidencia.group(1)) * (10 ** int(coincidencia.group(3)))
        return float(texto)

    def obtener_funciones(self, expresion):
        x, expr = crear_expresion(expresion)
        g_math = sp.lambdify(x, expr, "math")
        g_numpy = sp.lambdify(x, expr, "numpy")
        derivada = sp.diff(expr, x)
        gp_math = sp.lambdify(x, derivada, "math")
        return x, expr, derivada, g_math, gp_math, g_numpy

    def evaluar_seguro(self, funcion, valor, nombre="funcion"):
        try:
            resultado = float(funcion(valor))
        except ZeroDivisionError:
            raise ValueError(f"La {nombre} no se puede evaluar en x = {valor} porque hay division entre cero.")
        except Exception as error:
            raise ValueError(f"No se pudo evaluar la {nombre} en x = {valor}. Detalle: {error}")
        if not math.isfinite(resultado):
            raise ValueError(f"La {nombre} no tiene un valor finito en x = {valor}.")
        return resultado

    def calcular_max_iteraciones(self, g, gp, p0, tolerancia):
        p1 = self.evaluar_seguro(g, p0, "funcion g")
        error_inicial = abs(p1 - p0)
        if error_inicial <= tolerancia:
            return 1, "El primer paso ya cumple la tolerancia."

        try:
            muestras = np.linspace(min(p0, p1), max(p0, p1), 25)
            valores = [abs(float(gp(float(valor)))) for valor in muestras]
            valores = [valor for valor in valores if math.isfinite(valor)]
            k = max(valores) if valores else abs(float(gp(p0)))
        except Exception:
            k = None

        if k is not None and 0 < k < 1:
            argumento = tolerancia * (1 - k) / error_inicial
            if argumento <= 0:
                return 100, "No se pudo estimar una cota menor; se usa 100 iteraciones."
            n = math.ceil(math.log(argumento) / math.log(k))
            return max(1, n), f"Maximo calculado con contraccion k≈{redondear(k)}."

        return 100, "No se pudo asegurar |g'(x)|<1 para calcular una cota; se usa 100 iteraciones."

    def calcular_detallado(self, funcion, p0, tolerancia, max_iteraciones=None):
        x, expr, derivada, g, gp, g_numpy = self.obtener_funciones(funcion)
        p_anterior = self.convertir_numero(p0)
        tolerancia = self.convertir_numero(tolerancia)

        if tolerancia <= 0:
            raise ValueError("El error maximo debe ser mayor que cero.")

        max_raw = "" if max_iteraciones is None else str(max_iteraciones).strip()
        if max_raw:
            try:
                max_iteraciones = int(float(max_raw))
            except Exception:
                max_iteraciones = 100
            if max_iteraciones <= 0:
                max_iteraciones = 100
            aviso_iteraciones = "Maximo de iteraciones ingresado por el usuario."
        else:
            max_iteraciones, aviso_iteraciones = self.calcular_max_iteraciones(g, gp, p_anterior, tolerancia)

        tabla = []
        mensaje = "Se alcanzo el maximo de iteraciones."
        raiz = p_anterior

        for iteracion in range(1, max_iteraciones + 1):
            p_actual = self.evaluar_seguro(g, p_anterior, "funcion g")
            error = abs(p_actual - p_anterior)
            f_equivalente = p_actual - p_anterior

            tabla.append({
                "n": iteracion,
                "p_anterior": p_anterior,
                "g_p_anterior": p_actual,
                "error": error,
                "g(p)-p": f_equivalente,
            })

            raiz = p_actual
            if error <= tolerancia:
                mensaje = "Punto fijo aproximado encontrado dentro del error permitido."
                break
            p_anterior = p_actual

        aviso = ""
        try:
            gp_raiz = self.evaluar_seguro(gp, raiz, "derivada g'")
            if abs(gp_raiz) < 1:
                aviso = f" Cerca de la raiz |g'(x)| = {redondear(abs(gp_raiz))} < 1, por lo que la iteracion es contractiva localmente."
            else:
                aviso = f" Aviso: cerca de la raiz |g'(x)| = {redondear(abs(gp_raiz))} >= 1; puede no converger."
        except Exception:
            gp_raiz = None

        return {
            "expresion": str(expr),
            "derivada": str(derivada),
            "raiz": raiz,
            "mensaje": mensaje + aviso,
            "tabla": tabla,
            "funcion_numpy": g_numpy,
            "p0_inicial": self.convertir_numero(p0),
            "gp_raiz": gp_raiz,
            "max_iteraciones": max_iteraciones,
            "aviso_iteraciones": aviso_iteraciones,
        }

    def ejecutar(self, **kwargs):
        datos = self.calcular_detallado(
            funcion=kwargs.get("funcion"),
            p0=kwargs.get("p0"),
            tolerancia=kwargs.get("tolerancia"),
            max_iteraciones=kwargs.get("max_iteraciones"),
        )

        tabla = []
        for fila in datos["tabla"]:
            tabla.append({
                "n": fila["n"],
                "P_i": redondear(fila["p_anterior"]),
                "P_{i+1}=g(P_i)": redondear(fila["g_p_anterior"]),
                "Error": redondear(fila["error"]),
                "g(P_i)-P_i": redondear(fila["g(p)-p"]),
            })

        pasos = [
            "Se escribe la ecuacion en la forma x = g(x).",
            "Se toma un valor inicial P0.",
            f"{datos['aviso_iteraciones']} Maximo usado: {datos['max_iteraciones']}.",
            "Se calcula P_{i+1} = g(P_i).",
            "Se calcula el error como |P_{i+1} - P_i|.",
            "Se detiene cuando el error es menor o igual a la tolerancia.",
        ]

        mensaje = f"{datos['mensaje']} Maximo usado: {datos['max_iteraciones']}."

        return ResultadoMetodo(
            resultado=redondear(datos["raiz"]),
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla,
        )
