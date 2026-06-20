from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo
from core.funciones import crear_funcion_2_variables, redondear


class IntegralDobleSimpsonUnTercio(MetodoNumerico):
    nombre = "Integral doble (Simpson 1/3)"
    categoria = "Integración"
    descripcion = "Integral doble sobre [a,b]x[c,d] usando Simpson 1/3 en ambas direcciones (nx y ny deben ser pares)."

    parametros = [
        {"nombre": "funcion", "label": "Función f(x, y)", "tipo": "text", "placeholder": "x*y"},
        {"nombre": "a", "label": "x inferior a", "tipo": "number", "placeholder": "0"},
        {"nombre": "b", "label": "x superior b", "tipo": "number", "placeholder": "1"},
        {"nombre": "c", "label": "y inferior c", "tipo": "number", "placeholder": "0"},
        {"nombre": "d", "label": "y superior d", "tipo": "number", "placeholder": "1"},
        {"nombre": "nx", "label": "Divisiones en x (nx, par)", "tipo": "number", "placeholder": "4"},
        {"nombre": "ny", "label": "Divisiones en y (ny, par)", "tipo": "number", "placeholder": "4"},
    ]

    def ejecutar(self, **kwargs):
        expresion = kwargs.get("funcion")
        a = float(kwargs.get("a"))
        b = float(kwargs.get("b"))
        c = float(kwargs.get("c"))
        d = float(kwargs.get("d"))
        nx = int(kwargs.get("nx"))
        ny = int(kwargs.get("ny"))

        if nx % 2 != 0 or ny % 2 != 0 or nx < 2 or ny < 2:
            return ResultadoMetodo(
                resultado=None,
                mensaje="Para Simpson 1/3, nx y ny deben ser pares y mayores o iguales a 2.",
                pasos=[f"nx = {nx}, ny = {ny}: ambos deben ser pares."],
                tabla=[],
            )

        f = crear_funcion_2_variables(expresion)

        hx = (b - a) / nx
        hy = (d - c) / ny
        puntos_x = [a + i * hx for i in range(nx + 1)]
        puntos_y = [c + j * hy for j in range(ny + 1)]

        # Pesos de Simpson 1/3: 1 en extremos, 4 en impares, 2 en pares interiores
        def pesos_simpson(n):
            return [1 if (k == 0 or k == n) else (4 if k % 2 != 0 else 2) for k in range(n + 1)]

        pesos_x = pesos_simpson(nx)
        pesos_y = pesos_simpson(ny)

        suma = 0.0
        for i in range(nx + 1):
            for j in range(ny + 1):
                w = pesos_x[i] * pesos_y[j]
                suma += w * f(puntos_x[i], puntos_y[j])

        factor = (hx * hy) / 9
        resultado = factor * suma

        pasos = [
            f"nx = {nx}, ny = {ny} (ambos pares)",
            f"hx = (b - a)/nx = {redondear(hx)}, hy = (d - c)/ny = {redondear(hy)}",
            "Pesos en cada eje: 1 en extremos, 4 en impares, 2 en pares interiores.",
            f"I = (hx·hy/9)·ΣΣ(w·f(x,y)) = {redondear(resultado)}",
        ]

        return ResultadoMetodo(
            resultado=redondear(resultado),
            mensaje="Integral doble aproximada con Simpson 1/3.",
            pasos=pasos,
            tabla=[],
        )
