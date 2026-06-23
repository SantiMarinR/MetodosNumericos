from core.funciones import crear_funcion, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from metodos.integracion.legendre_simple import GAUSS_DATA


class LegendreCompuesto(MetodoNumerico):
    nombre = "Cuadratura de Gauss-Legendre compuesta"
    categoria = "Integración"
    descripcion = "Divide [a, b] en n subintervalos y aplica Gauss-Legendre en cada uno."

    parametros = [
        {"nombre": "funcion", "label": "Funcion f(x)", "tipo": "text", "placeholder": "x**2"},
        {"nombre": "a", "label": "Limite inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "Limite superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "puntos", "label": "Numero de puntos (2 a 5)", "tipo": "number", "placeholder": "3"},
        {"nombre": "n", "label": "Numero de subintervalos n", "tipo": "number", "placeholder": "4"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        puntos = int(kwargs.get("puntos"))
        n = int(kwargs.get("n"))

        if puntos not in GAUSS_DATA:
            return ResultadoMetodo(None, "Numero de puntos no soportado. Usa 2, 3, 4 o 5.", [f"puntos = {puntos} no es valido."], [])
        if n < 1:
            return ResultadoMetodo(None, "El numero de subintervalos n debe ser al menos 1.", [f"n = {n} no es valido."], [])

        f = crear_funcion(expresion)
        nodos, pesos = GAUSS_DATA[puntos]

        h = (b - a) / n
        integral_total = 0.0
        tabla = []
        pasos = [
            f"Se divide el intervalo en n={n} subintervalos con h=(b-a)/n={redondear(h)}.",
            f"En cada subintervalo se aplica Gauss-Legendre de {puntos} puntos.",
        ]

        for i in range(n):
            sub_a = a + i * h
            sub_b = sub_a + h
            suma_sub = 0.0
            pasos.append(f"Subintervalo {i + 1}: [{redondear(sub_a)}, {redondear(sub_b)}].")
            for k, (nodo, peso) in enumerate(zip(nodos, pesos), start=1):
                x_trans = 0.5 * ((sub_b - sub_a) * nodo + (sub_b + sub_a))
                fx = f(x_trans)
                aporte = peso * fx
                suma_sub += aporte
                tabla.append({
                    "sub": i + 1,
                    "k": k,
                    "a_i": redondear(sub_a),
                    "b_i": redondear(sub_b),
                    "nodo t": redondear(nodo),
                    "peso w": redondear(peso),
                    "x": redondear(x_trans),
                    "f(x)": redondear(fx),
                    "w*f(x)": redondear(aporte),
                })
                if i < 10:
                    pasos.append(
                        f"  Nodo {k}: x={redondear(x_trans)}, w*f(x)={redondear(peso)}*{redondear(fx)}={redondear(aporte)}."
                    )
            parcial = 0.5 * (sub_b - sub_a) * suma_sub
            integral_total += parcial
            tabla.append({
                "sub": i + 1,
                "k": "parcial",
                "a_i": redondear(sub_a),
                "b_i": redondear(sub_b),
                "nodo t": "",
                "peso w": "",
                "x": "",
                "f(x)": "",
                "w*f(x)": redondear(parcial),
            })
            if i < 10:
                pasos.append(
                    f"  I_{i + 1}=0.5*({redondear(sub_b)}-{redondear(sub_a)})*{redondear(suma_sub)}={redondear(parcial)}."
                )

        if n > 10:
            pasos.append("Se omiten del procedimiento escrito algunos subintervalos para no saturar la pantalla; la tabla conserva todos los valores.")
        pasos.append(f"I total = suma de parciales = {redondear(integral_total)}.")

        return ResultadoMetodo(
            resultado=redondear(integral_total),
            mensaje="Integral aproximada con Gauss-Legendre compuesta.",
            pasos=pasos,
            tabla=tabla,
        )
