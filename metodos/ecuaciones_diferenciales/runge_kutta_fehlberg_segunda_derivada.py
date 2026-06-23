from metodos.ecuaciones_diferenciales.sistema_edo_primer_orden import crear_funcion_3_variables
from core.funciones import redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class RungeKuttaFehlbergSegundaDerivada(MetodoNumerico):
    nombre = "Runge-Kutta-Fehlberg segunda derivada"
    categoria = "Ecuaciones diferenciales"
    descripcion = (
        "Aplica RKF45 a y'' = f(t,y,y') convirtiendo a sistema con z=y'. "
        "Muestra estimacion de error local para y y z."
    )

    parametros = [
        {"nombre": "funcion_z", "label": "Funcion f(t,y,z)=y'' con z=y'", "tipo": "text", "placeholder": "-y"},
        {"nombre": "x0", "label": "Valor inicial t0", "tipo": "number", "placeholder": "0"},
        {"nombre": "y0", "label": "Valor inicial y(t0)", "tipo": "number", "placeholder": "1"},
        {"nombre": "z0", "label": "Valor inicial y'(t0)", "tipo": "number", "placeholder": "0"},
        {"nombre": "h", "label": "Paso h", "tipo": "number", "placeholder": "0.1"},
        {"nombre": "n", "label": "Numero de pasos n", "tipo": "number", "placeholder": "10"},
    ]

    def ejecutar(self, **kwargs):
        g = crear_funcion_3_variables(kwargs.get("funcion_z"))
        t = float(kwargs.get("x0"))
        y = float(kwargs.get("y0"))
        z = float(kwargs.get("z0"))
        h = float(kwargs.get("h"))
        n = int(float(kwargs.get("n")))

        if h == 0 or n < 1:
            return ResultadoMetodo(None, "h debe ser distinto de 0 y n debe ser mayor o igual a 1.", [], [])

        tabla = []
        for i in range(1, n + 1):
            def F(tt, yy, zz):
                return zz, g(tt, yy, zz)

            def comb(base, coefs, ks):
                return base + sum(c * k for c, k in zip(coefs, ks))

            k1y, k1z = [h * v for v in F(t, y, z)]
            k2y, k2z = [h * v for v in F(t + h / 4, y + k1y / 4, z + k1z / 4)]
            k3y, k3z = [h * v for v in F(
                t + 3 * h / 8,
                y + 3 * k1y / 32 + 9 * k2y / 32,
                z + 3 * k1z / 32 + 9 * k2z / 32,
            )]
            k4y, k4z = [h * v for v in F(
                t + 12 * h / 13,
                y + 1932 * k1y / 2197 - 7200 * k2y / 2197 + 7296 * k3y / 2197,
                z + 1932 * k1z / 2197 - 7200 * k2z / 2197 + 7296 * k3z / 2197,
            )]
            k5y, k5z = [h * v for v in F(
                t + h,
                y + 439 * k1y / 216 - 8 * k2y + 3680 * k3y / 513 - 845 * k4y / 4104,
                z + 439 * k1z / 216 - 8 * k2z + 3680 * k3z / 513 - 845 * k4z / 4104,
            )]
            k6y, k6z = [h * v for v in F(
                t + h / 2,
                y - 8 * k1y / 27 + 2 * k2y - 3544 * k3y / 2565 + 1859 * k4y / 4104 - 11 * k5y / 40,
                z - 8 * k1z / 27 + 2 * k2z - 3544 * k3z / 2565 + 1859 * k4z / 4104 - 11 * k5z / 40,
            )]

            y4 = y + 25 * k1y / 216 + 1408 * k3y / 2565 + 2197 * k4y / 4104 - k5y / 5
            z4 = z + 25 * k1z / 216 + 1408 * k3z / 2565 + 2197 * k4z / 4104 - k5z / 5
            y5 = y + 16 * k1y / 135 + 6656 * k3y / 12825 + 28561 * k4y / 56430 - 9 * k5y / 50 + 2 * k6y / 55
            z5 = z + 16 * k1z / 135 + 6656 * k3z / 12825 + 28561 * k4z / 56430 - 9 * k5z / 50 + 2 * k6z / 55

            tabla.append({
                "i": i, "t_i": redondear(t), "y_i": redondear(y), "z_i=y'_i": redondear(z),
                "y orden 4": redondear(y4), "y orden 5": redondear(y5),
                "z orden 4": redondear(z4), "z orden 5": redondear(z5),
                "error y": redondear(abs(y5 - y4)), "error z": redondear(abs(z5 - z4)),
            })
            t, y, z = t + h, y5, z5

        return ResultadoMetodo(
            resultado={"x": redondear(t), "y": redondear(y), "z": redondear(z)},
            mensaje=f"Aproximacion final RKF45: y({redondear(t)})={redondear(y)}, y'({redondear(t)})={redondear(z)}",
            pasos=[
                "Se transforma y''=f(t,y,y') en sistema con z=y'.",
                "Se aplica Fehlberg RKF45 al sistema y se comparan orden 4 y orden 5.",
                "El error local se estima con las diferencias entre ambos ordenes.",
            ],
            tabla=tabla,
        )
