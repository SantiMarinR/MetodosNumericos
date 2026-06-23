from core.funciones import crear_funcion_2_variables, redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class RungeKuttaFehlberg(MetodoNumerico):
    nombre = "Runge-Kutta-Fehlberg"
    categoria = "Ecuaciones diferenciales"
    descripcion = "Aplica RKF45 para y'=f(x,y), calculando aproximaciones de orden 4 y 5 y el error local."

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
            k2 = h * f(x + h / 4, y + k1 / 4)
            k3 = h * f(x + 3 * h / 8, y + 3 * k1 / 32 + 9 * k2 / 32)
            k4 = h * f(x + 12 * h / 13, y + 1932 * k1 / 2197 - 7200 * k2 / 2197 + 7296 * k3 / 2197)
            k5 = h * f(x + h, y + 439 * k1 / 216 - 8 * k2 + 3680 * k3 / 513 - 845 * k4 / 4104)
            k6 = h * f(x + h / 2, y - 8 * k1 / 27 + 2 * k2 - 3544 * k3 / 2565 + 1859 * k4 / 4104 - 11 * k5 / 40)

            y4 = y + 25 * k1 / 216 + 1408 * k3 / 2565 + 2197 * k4 / 4104 - k5 / 5
            y5 = y + 16 * k1 / 135 + 6656 * k3 / 12825 + 28561 * k4 / 56430 - 9 * k5 / 50 + 2 * k6 / 55
            error = abs(y5 - y4)
            tabla.append({
                "i": i, "x_i": redondear(x), "y_i": redondear(y),
                "k1": redondear(k1), "k2": redondear(k2), "k3": redondear(k3),
                "k4": redondear(k4), "k5": redondear(k5), "k6": redondear(k6),
                "y orden 4": redondear(y4), "y orden 5": redondear(y5), "error": redondear(error),
            })
            x, y = x + h, y5

        return ResultadoMetodo(
            resultado={"x": redondear(x), "y": redondear(y)},
            mensaje=f"Aproximacion final RKF45: y({redondear(x)}) = {redondear(y)}",
            pasos=[
                "Se calculan k1 a k6 con los coeficientes de Fehlberg.",
                "Se obtiene y de orden 4 y y de orden 5.",
                "El error local se estima como |y_5 - y_4|.",
            ],
            tabla=tabla,
        )
