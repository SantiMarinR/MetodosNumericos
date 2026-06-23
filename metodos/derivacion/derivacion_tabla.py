from core.funciones import redondear, texto_a_lista_numeros
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class DerivacionTabla(MetodoNumerico):
    nombre = "Derivación con tabla"
    categoria = "Derivación"
    descripcion = "Calcula f'(x) usando una tabla de valores x_i, y_i y formulas de 2, 3 o 5 puntos."

    parametros = [
        {"nombre": "xs", "label": "Valores de x", "tipo": "text", "placeholder": "1.8, 1.9, 2.0, 2.1, 2.2"},
        {"nombre": "ys", "label": "Valores de y", "tipo": "text", "placeholder": "6.0496, 6.6858, 7.3891, 8.1662, 9.0250"},
        {"nombre": "x", "label": "Punto donde derivar", "tipo": "number", "placeholder": "2.0"},
        {"nombre": "formula", "label": "Formula", "tipo": "text", "placeholder": "5 central"},
    ]

    def ejecutar(self, **kwargs):
        try:
            xs = texto_a_lista_numeros(kwargs.get("xs"))
            ys = texto_a_lista_numeros(kwargs.get("ys"))
            x0 = float(kwargs.get("x"))
        except Exception:
            return ResultadoMetodo(None, "Los valores de x, y y el punto deben ser numericos.", [], [])

        if len(xs) != len(ys) or len(xs) < 2:
            return ResultadoMetodo(None, "La tabla debe tener la misma cantidad de x_i y y_i, con al menos 2 puntos.", [], [])
        if len(set(xs)) != len(xs):
            return ResultadoMetodo(None, "No se permiten valores x repetidos.", [], [])

        pares = sorted(zip(xs, ys), key=lambda p: p[0])
        xs = [p[0] for p in pares]
        ys = [p[1] for p in pares]
        h = xs[1] - xs[0]
        if h == 0:
            return ResultadoMetodo(None, "El paso h no puede ser 0.", [], [])
        for i in range(1, len(xs) - 1):
            if abs((xs[i + 1] - xs[i]) - h) > 1e-7:
                return ResultadoMetodo(None, "Para estas formulas la tabla debe estar igualmente espaciada.", [], [])

        indice = None
        for i, xi in enumerate(xs):
            if abs(xi - x0) <= 1e-7:
                indice = i
                break
        if indice is None:
            return ResultadoMetodo(None, "El punto donde derivar debe existir en la tabla de x_i.", [], [])

        formula = str(kwargs.get("formula") or "5 central").strip().lower()
        if "5" in formula:
            puntos = 5
        elif "3" in formula:
            puntos = 3
        else:
            puntos = 2

        if "adelante" in formula:
            direccion = "adelante"
        elif "atras" in formula:
            direccion = "atras"
        else:
            direccion = "central"

        try:
            derivada, usados, formula_txt, denominador = self._calcular(xs, ys, indice, h, puntos, direccion)
        except ValueError as error:
            return ResultadoMetodo(None, str(error), [], [])

        tabla = [["punto", "x", "y", "coef"]]
        numerador = 0.0
        for etiqueta, xi, yi, coef in usados:
            tabla.append([etiqueta, redondear(xi), redondear(yi), coef])
            numerador += coef * yi
        tabla.append(["-", "h", redondear(h), ""])
        tabla.append(["-", "numerador", redondear(numerador), ""])
        tabla.append(["-", "denominador", redondear(denominador), ""])
        tabla.append(["-", "f'(x)", redondear(derivada), ""])

        sustitucion = " + ".join(
            f"({coef})*{redondear(yi)}" for _etiqueta, _xi, yi, coef in usados
        )
        puntos_usados = ", ".join(
            f"{etiqueta}=({redondear(xi)}, {redondear(yi)})" for etiqueta, xi, yi, _coef in usados
        )

        pasos = [
            "Se ordena la tabla por x_i y se verifica que el paso h sea constante.",
            f"Como h = {redondear(h)}, se usa la formula de {puntos} puntos hacia {direccion}: {formula_txt}.",
            f"Puntos usados: {puntos_usados}.",
            f"Numerador = {sustitucion} = {redondear(numerador)}.",
            f"f'({redondear(x0)}) = numerador / denominador = {redondear(numerador)} / {redondear(denominador)} = {redondear(derivada)}.",
        ]

        return ResultadoMetodo(
            resultado={"x": redondear(x0), "derivada_aprox": redondear(derivada), "h": redondear(h)},
            mensaje=f"f'({redondear(x0)}) aprox {redondear(derivada)} con {puntos} puntos ({direccion}).",
            pasos=pasos,
            tabla=tabla,
        )

    def _calcular(self, xs, ys, i, h, puntos, direccion):
        def require(indices):
            if min(indices) < 0 or max(indices) >= len(xs):
                raise ValueError("No hay suficientes puntos en la tabla para esa formula.")

        if puntos == 2:
            if direccion == "adelante":
                idx, coefs, denom, formula = [i, i + 1], [-1, 1], h, "[f(x+h)-f(x)]/h"
            elif direccion == "atras":
                idx, coefs, denom, formula = [i - 1, i], [-1, 1], h, "[f(x)-f(x-h)]/h"
            else:
                idx, coefs, denom, formula = [i - 1, i + 1], [-1, 1], 2 * h, "[f(x+h)-f(x-h)]/(2h)"
        elif puntos == 3:
            if direccion == "adelante":
                idx, coefs, denom, formula = [i, i + 1, i + 2], [-3, 4, -1], 2 * h, "[-3f(x)+4f(x+h)-f(x+2h)]/(2h)"
            elif direccion == "atras":
                idx, coefs, denom, formula = [i, i - 1, i - 2], [3, -4, 1], 2 * h, "[3f(x)-4f(x-h)+f(x-2h)]/(2h)"
            else:
                idx, coefs, denom, formula = [i - 1, i + 1], [-1, 1], 2 * h, "[f(x+h)-f(x-h)]/(2h)"
        else:
            if direccion == "adelante":
                idx, coefs, denom, formula = [i, i + 1, i + 2, i + 3, i + 4], [-25, 48, -36, 16, -3], 12 * h, "[-25f(x)+48f(x+h)-36f(x+2h)+16f(x+3h)-3f(x+4h)]/(12h)"
            elif direccion == "atras":
                idx, coefs, denom, formula = [i, i - 1, i - 2, i - 3, i - 4], [25, -48, 36, -16, 3], 12 * h, "[25f(x)-48f(x-h)+36f(x-2h)-16f(x-3h)+3f(x-4h)]/(12h)"
            else:
                idx, coefs, denom, formula = [i - 2, i - 1, i + 1, i + 2], [1, -8, 8, -1], 12 * h, "[f(x-2h)-8f(x-h)+8f(x+h)-f(x+2h)]/(12h)"

        require(idx)
        usados = [(f"x{j}", xs[j], ys[j], c) for j, c in zip(idx, coefs)]
        derivada = sum(c * ys[j] for j, c in zip(idx, coefs)) / denom
        return derivada, usados, formula, denom
