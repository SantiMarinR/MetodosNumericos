from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion_2_variables, redondear


class IntegralDobleTrapecio(MetodoNumerico):
    nombre = "Integral doble (Trapecio)"
    categoria = "Integración"
    descripcion = "Integral doble sobre una región rectangular [a,b]x[c,d] usando la regla del trapecio en ambas direcciones."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x, y)", "tipo": "text", "placeholder": "x*y"},
        {"nombre": "a", "label": "x inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "x superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "c", "label": "y inferior c", "tipo": "number", "placeholder": "0"},
        {"nombre": "d", "label": "y superior d", "tipo": "number", "placeholder": "1"},
        {"nombre": "nx", "label": "Divisiones en x (nx)", "tipo": "number", "placeholder": "4"},
        {"nombre": "ny", "label": "Divisiones en y (ny)", "tipo": "number", "placeholder": "4"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        c = float(kwargs.get("c"))
        d = float(kwargs.get("d"))
        nx = int(kwargs.get("nx"))
        ny = int(kwargs.get("ny"))

        if nx < 1 or ny < 1:
            return ResultadoMetodo(
                resultado=None,
                mensaje="nx y ny deben ser al menos 1.",
                pasos=["Corrige los valores de nx y ny."],
                tabla=[],
            )

        f = crear_funcion_2_variables(expresion)

        hx = (b - a) / nx
        hy = (d - c) / ny
        puntos_x = [a + i * hx for i in range(nx + 1)]
        puntos_y = [c + j * hy for j in range(ny + 1)]

        # Pesos de trapecio: 1 en los extremos, 2 en el interior
        pesos_x = [1 if (i == 0 or i == nx) else 2 for i in range(nx + 1)]
        pesos_y = [1 if (j == 0 or j == ny) else 2 for j in range(ny + 1)]

        suma = 0.0
        for i in range(nx + 1):
            for j in range(ny + 1):
                w = pesos_x[i] * pesos_y[j]
                suma += w * f(puntos_x[i], puntos_y[j])

        factor = (hx * hy) / 4
        resultado = factor * suma

        pasos = [
            f"hx = (b - a)/nx = {redondear(hx)}, hy = (d - c)/ny = {redondear(hy)}",
            "Pesos en cada eje: 1 en los extremos, 2 en el interior.",
            f"I = (hx·hy/4)·ΣΣ(w·f(x,y)) = {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral doble aproximada con trapecio.",
            pasos=pasos,
            tabla=[],
        )