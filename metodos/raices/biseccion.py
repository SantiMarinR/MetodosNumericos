from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion, redondear


class Biseccion(MetodoNumerico):
    nombre = "Biseccion"
    categoria = "Raíces de ecuaciones"
    descripcion = "Método que aproxima una raíz dividiendo un intervalo [a,b] donde existe cambio de signo."

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
            "label": "Tolerancia",
            "tipo": "number",
            "placeholder": "0.0001"
        },
        {
            "nombre": "max_iteraciones",
            "label": "Máximo de iteraciones",
            "tipo": "number",
            "placeholder": "100"
        },
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        tolerancia = float(kwargs.get("tolerancia"))
        max_iteraciones = int(kwargs.get("max_iteraciones"))

        f = crear_funcion(expresion)

        if f(a) * f(b) >= 0:
            return ResultadoMetodo(
                resultado=None,
                mensaje="El intervalo no cumple con cambio de signo. Prueba con otros valores de a y b.",
                pasos=[
                    f"f(a) = f({a}) = {redondear(f(a))}",
                    f"f(b) = f({b}) = {redondear(f(b))}",
                    "Para usar bisección se necesita que f(a) y f(b) tengan signos opuestos."
                ],
                tabla=[]
            )

        tabla = []
        pasos = []

        pasos.append("Se verifica que exista cambio de signo en el intervalo.")
        pasos.append(f"Intervalo inicial: [{a}, {b}]")
        pasos.append(f"Tolerancia: {tolerancia}")

        raiz = None

        for i in range(1, max_iteraciones + 1):
            c = (a + b) / 2
            fa = f(a)
            fb = f(b)
            fc = f(c)
            error = abs(b - a) / 2

            tabla.append({
                "Iteración": i,
                "a": redondear(a),
                "b": redondear(b),
                "c": redondear(c),
                "f(a)": redondear(fa),
                "f(b)": redondear(fb),
                "f(c)": redondear(fc),
                "Error": redondear(error)
            })

            if abs(fc) < tolerancia or error < tolerancia:
                raiz = c
                pasos.append(f"Se detuvo en la iteración {i} porque el error ya es menor que la tolerancia.")
                break

            if fa * fc < 0:
                b = c
            else:
                a = c

        if raiz is None:
            raiz = c
            mensaje = "Se alcanzó el máximo de iteraciones."
        else:
            mensaje = "Raíz aproximada encontrada correctamente."

        return ResultadoMetodo(
            resultado=redondear(raiz),
            mensaje=mensaje,
            pasos=pasos,
            tabla=tabla
        )