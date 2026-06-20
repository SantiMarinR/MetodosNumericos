import re
import sympy as sp
import numpy as np

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class Lagrange(MetodoNumerico):
    nombre = "Lagrange"
    categoria = "Interpolación"
    descripcion = "Interpolación polinómica de Lagrange evaluando yᵢ = f(xᵢ)."

    parametros = [
        {
            "nombre": "funcion",
            "label": "Función f(x)",
            "tipo": "text",
            "placeholder": "Ejemplo: x**2 + 2*x + 1"
        },
        {
            "nombre": "puntos_x",
            "label": "Valores de x separados por coma",
            "tipo": "text",
            "placeholder": "Ejemplo: 0, 1, 2"
        },
    ]

    # =========================================================
    # CONVERSIONES Y FORMATO
    # =========================================================

    def convertir_valor(self, texto):
        texto = str(texto).strip()
        texto = texto.replace(",", ".")

        if texto == "":
            raise ValueError("Hay un valor vacío en la tabla de puntos.")

        locales = {
            "pi": sp.pi,
            "e": sp.E,
            "sqrt": sp.sqrt,
        }

        try:
            return sp.Rational(texto)
        except Exception:
            try:
                return sp.nsimplify(sp.sympify(texto, locals=locales))
            except Exception:
                raise ValueError(f"No se pudo interpretar el valor: {texto}")

    def preparar_expresion(self, expresion):
        expresion = str(expresion).strip()

        if not expresion:
            raise ValueError("Escribe una función f(x) antes de calcular.")

        expresion = expresion.replace(" ", "")
        expresion = expresion.replace("^", "**")
        expresion = expresion.replace("sen", "sin")
        expresion = expresion.replace("ln", "log")

        # Multiplicaciones implícitas comunes:
        # 2x -> 2*x, 2(x+1) -> 2*(x+1), xcos(x) -> x*cos(x)
        expresion = re.sub(r"(\d)(x)", r"\1*\2", expresion)
        expresion = re.sub(r"(\d)(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(\d)(sin|cos|tan|log|exp|sqrt)", r"\1*\2", expresion)
        expresion = re.sub(r"(x)(sin|cos|tan|log|exp|sqrt)", r"\1*\2", expresion)
        expresion = re.sub(r"(x)(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(\))(\()", r"\1*\2", expresion)
        expresion = re.sub(r"(\))(sin|cos|tan|log|exp|sqrt|x)", r"\1*\2", expresion)

        return expresion

    def obtener_funcion(self, expresion):
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
            funcion = sp.sympify(expresion, locals=locales)
        except Exception:
            raise ValueError(
                "La función no se pudo interpretar. Revisa paréntesis, multiplicaciones y operadores."
            )

        return x, sp.simplify(funcion)

    def formatear_expr(self, expresion):
        return sp.sstr(sp.simplify(expresion))

    def formatear_decimal(self, expresion, decimales=6):
        try:
            return f"{float(sp.N(expresion, 15)):.{decimales}f}"
        except Exception:
            return self.formatear_expr(expresion)

    def formatear_x_factor(self, valor):
        """Regresa factor bonito: (x - 1.800000) o (x + 1.800000)."""
        valor_decimal = float(sp.N(valor, 15))

        if valor_decimal < 0:
            return f"(x + {abs(valor_decimal):.6f})"

        return f"(x - {valor_decimal:.6f})"

    def parsear_x_texto(self, puntos_x_texto):
        texto = str(puntos_x_texto).strip()

        if not texto:
            raise ValueError("Escribe los valores de x separados por coma. Ejemplo: 0, 1, 2")

        partes = [parte.strip() for parte in texto.split(",") if parte.strip()]
        return partes

    def evaluar_y(self, funcion_simbolica, variable, xi):
        """Evalúa yᵢ = f(xᵢ) y lo devuelve como número decimal, no como expresión simbólica."""
        yi = funcion_simbolica.subs(variable, xi)
        yi_decimal = float(sp.N(yi, 15))
        return sp.Float(yi_decimal, 12)

    # =========================================================
    # CALCULO DETALLADO
    # =========================================================

    def calcular_detallado(self, funcion=None, valores_x=None, puntos_x_texto=None, puntos=None):
        x = sp.symbols("x")
        funcion_original_numpy = None

        # Compatibilidad: si se mandan puntos (x,y), también funciona.
        if puntos is not None and funcion is None:
            if len(puntos) < 2:
                raise ValueError("Necesitas al menos 2 puntos para construir un polinomio de Lagrange.")

            puntos_exactos = []
            for indice, punto in enumerate(puntos):
                if len(punto) != 2:
                    raise ValueError(f"El punto {indice + 1} debe tener x y y.")
                xi = self.convertir_valor(punto[0])
                yi = sp.Float(float(sp.N(self.convertir_valor(punto[1]), 15)), 12)
                puntos_exactos.append((xi, yi))

            funcion_simbolica = None
            funcion_texto = "No se proporcionó función; se usaron yᵢ dados."
        else:
            x, funcion_simbolica = self.obtener_funcion(funcion)
            funcion_original_numpy = sp.lambdify(x, funcion_simbolica, "numpy")

            if valores_x is None:
                valores_x = self.parsear_x_texto(puntos_x_texto)

            if len(valores_x) < 2:
                raise ValueError("Necesitas al menos 2 valores de x para construir un polinomio de Lagrange.")

            puntos_exactos = []
            for valor_x in valores_x:
                xi = self.convertir_valor(valor_x)
                yi = self.evaluar_y(funcion_simbolica, x, xi)
                puntos_exactos.append((xi, yi))

            funcion_texto = self.formatear_expr(funcion_simbolica)

        valores_x = [sp.simplify(p[0]) for p in puntos_exactos]
        valores_x_texto = [sp.sstr(valor) for valor in valores_x]

        if len(set(valores_x_texto)) != len(valores_x_texto):
            raise ValueError("No se pueden repetir valores de x. Cada xᵢ debe ser diferente.")

        terminos = []
        tabla = []
        pasos = []

        if funcion is not None:
            pasos.append(f"Se toma la función f(x) = {funcion_texto}.")
            pasos.append("Se evalúa cada xᵢ en la función para obtener yᵢ = f(xᵢ).")
        else:
            pasos.append("Se toman los puntos (xᵢ, yᵢ) dados por el usuario.")

        pasos.append("Se construye cada base Lᵢ(x) con productos de (x - xⱼ)/(xᵢ - xⱼ), con j diferente de i.")
        pasos.append("El polinomio final se obtiene con P(x) = Σ yᵢ Lᵢ(x).")

        for i, (xi, yi) in enumerate(puntos_exactos):
            numerador = sp.Integer(1)
            denominador = sp.Integer(1)
            factores_numerador = []

            for j, (xj, yj) in enumerate(puntos_exactos):
                if i == j:
                    continue

                numerador *= (x - xj)
                denominador *= (xi - xj)
                factores_numerador.append(self.formatear_x_factor(xj))

            Li = sp.simplify(numerador / denominador)
            Li_expandido = sp.expand(Li)
            termino = sp.simplify(yi * Li)
            terminos.append(termino)

            denominador_decimal = float(sp.N(denominador, 15))
            numerador_texto = "".join(factores_numerador)
            Li_producto_texto = f"{numerador_texto} / ({denominador_decimal:.6f})"
            Li_expandido_texto = sp.sstr(sp.N(Li_expandido, 8))

            tabla.append({
                "i": i,
                "xi": xi,
                "yi": yi,
                "Li": Li,
                "Li_expandido": Li_expandido,
                "Li_producto_texto": Li_producto_texto,
                "Li_expandido_texto": Li_expandido_texto,
                "denominador": denominador,
                "denominador_decimal": denominador_decimal,
                "termino": termino,
            })

            pasos.append(
                f"y_{i} = f({self.formatear_decimal(xi, 6)}) = {self.formatear_decimal(yi, 6)}. "
                f"L_{i}(x) = {Li_producto_texto}."
            )

        polinomio_lagrange = sp.simplify(sum(terminos))
        polinomio_expandido = sp.expand(polinomio_lagrange)
        polinomio_factorizado = sp.factor(polinomio_expandido)

        puntos_float = []
        for xi, yi in puntos_exactos:
            puntos_float.append((float(sp.N(xi, 15)), float(sp.N(yi, 15))))

        polinomio_numpy = sp.lambdify(x, polinomio_expandido, "numpy")

        return {
            "mensaje": "Polinomio de Lagrange calculado correctamente.",
            "funcion_texto": funcion_texto,
            "puntos": puntos_exactos,
            "puntos_float": puntos_float,
            "tabla": tabla,
            "pasos": pasos,
            "polinomio_lagrange": polinomio_lagrange,
            "polinomio_expandido": polinomio_expandido,
            "polinomio_factorizado": polinomio_factorizado,
            "polinomio_texto": sp.sstr(sp.N(polinomio_expandido, 10)),
            "polinomio_lagrange_texto": sp.sstr(sp.N(polinomio_lagrange, 10)),
            "polinomio_factorizado_texto": sp.sstr(sp.N(polinomio_factorizado, 10)),
            "funcion_numpy": polinomio_numpy,
            "polinomio_numpy": polinomio_numpy,
            "funcion_original_numpy": funcion_original_numpy,
        }

    # =========================================================
    # EJECUCION NORMAL
    # =========================================================

    def ejecutar(self, **kwargs):
        funcion = kwargs.get("funcion")
        puntos_x_texto = kwargs.get("puntos_x")

        datos = self.calcular_detallado(
            funcion=funcion,
            puntos_x_texto=puntos_x_texto,
        )

        tabla = []
        for fila in datos["tabla"]:
            tabla.append({
                "i": fila["i"],
                "x_i": self.formatear_decimal(fila["xi"], 6),
                "y_i = f(x_i)": self.formatear_decimal(fila["yi"], 6),
                "L_i(x)": fila["Li_producto_texto"],
                "L_i(x) expandido": fila["Li_expandido_texto"],
            })

        return ResultadoMetodo(
            resultado=datos["polinomio_texto"],
            mensaje=datos["mensaje"],
            pasos=datos["pasos"],
            tabla=tabla
        )
