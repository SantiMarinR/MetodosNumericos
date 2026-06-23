from core.funciones import crear_funcion_2_variables, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class RungeKutta4(MetodoNumerico):
    nombre = "Runge-Kutta 4"
    categoria = "Ecuaciones diferenciales"
    descripcion = "Resuelve y' = f(x,y) con el metodo clasico de Runge-Kutta de cuarto orden."

    parametros = [
        {"nombre": "funcion", "label": "Funcion f(x,y) = y'", "tipo": "text", "placeholder": "x + y"},
        {"nombre": "x0", "label": "Valor inicial x0", "tipo": "number", "placeholder": "0"},
        {"nombre": "y0", "label": "Valor inicial y0", "tipo": "number", "placeholder": "1"},
        {"nombre": "h", "label": "Paso h", "tipo": "number", "placeholder": "0.1"},
        {"nombre": "n", "label": "Numero de pasos n", "tipo": "number", "placeholder": "10"},
    ]

    def ejecutar(self, **kwargs):
        f = crear_funcion_2_variables(kwargs.get("funcion"))
        x = float(kwargs.get("x0"))
        y = float(kwargs.get("y0"))
        h = float(kwargs.get("h"))
        n = int(float(kwargs.get("n")))

        if h == 0 or n < 1:
            return ResultadoMetodo(None, "h debe ser distinto de 0 y n debe ser mayor o igual a 1.", [], [])

        tabla = []
        for i in range(1, n + 1):
            k1 = h * f(x, y)
            k2 = h * f(x + h / 2, y + k1 / 2)
            k3 = h * f(x + h / 2, y + k2 / 2)
            k4 = h * f(x + h, y + k3)
            y_sig = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            x_sig = x + h
            tabla.append({
                "i": i,
                "x_i": redondear(x),
                "y_i": redondear(y),
                "k1": redondear(k1),
                "k2": redondear(k2),
                "k3": redondear(k3),
                "k4": redondear(k4),
                "y_{i+1}": redondear(y_sig),
            })
            x, y = x_sig, y_sig

        pasos = [
            "Se calcula k1 = h*f(x_i,y_i).",
            "Se calcula k2 = h*f(x_i+h/2, y_i+k1/2).",
            "Se calcula k3 = h*f(x_i+h/2, y_i+k2/2).",
            "Se calcula k4 = h*f(x_i+h, y_i+k3).",
            "Se actualiza y_{i+1}=y_i+(k1+2k2+2k3+k4)/6.",
        ]

        return ResultadoMetodo(
            resultado={"x": redondear(x), "y": redondear(y)},
            mensaje=f"Aproximacion final: y({redondear(x)}) = {redondear(y)}",
            pasos=pasos,
            tabla=tabla,
        )
