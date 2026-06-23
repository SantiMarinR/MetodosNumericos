from metodos.ecuaciones_diferenciales.sistema_edo_primer_orden import crear_funcion_3_variables
from core.funciones import redondear
from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class RungeKutta4SegundaDerivada(MetodoNumerico):
    nombre = "Runge-Kutta 4 segunda derivada"
    categoria = "Ecuaciones diferenciales"
    descripcion = (
        "Resuelve y'' = f(t,y,y') con RK4 convirtiendo a sistema: "
        "z=y', y'=z, z'=f(t,y,z)."
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
        pasos = [
            "Se transforma la ecuacion y'' = f(t,y,y') en un sistema de primer orden.",
            "Se define z = y', por eso y' = z y z' = f(t,y,z).",
            "Se aplica RK4 simultaneamente a y y z.",
        ]
        for i in range(1, n + 1):
            k1y = h * z
            k1z = h * g(t, y, z)
            k2y = h * (z + k1z / 2)
            k2z = h * g(t + h / 2, y + k1y / 2, z + k1z / 2)
            k3y = h * (z + k2z / 2)
            k3z = h * g(t + h / 2, y + k2y / 2, z + k2z / 2)
            k4y = h * (z + k3z)
            k4z = h * g(t + h, y + k3y, z + k3z)

            y_sig = y + (k1y + 2 * k2y + 2 * k3y + k4y) / 6
            z_sig = z + (k1z + 2 * k2z + 2 * k3z + k4z) / 6

            tabla.append({
                "i": i, "t_i": redondear(t), "y_i": redondear(y), "z_i=y'_i": redondear(z),
                "k1y": redondear(k1y), "k2y": redondear(k2y), "k3y": redondear(k3y), "k4y": redondear(k4y),
                "k1z": redondear(k1z), "k2z": redondear(k2z), "k3z": redondear(k3z), "k4z": redondear(k4z),
                "t_{i+1}": redondear(t + h), "y_{i+1}": redondear(y_sig), "z_{i+1}": redondear(z_sig),
            })
            if i <= 20:
                pasos.extend([
                    f"Iteracion {i}: t_i={redondear(t)}, y_i={redondear(y)}, z_i=y'_i={redondear(z)}.",
                    f"k1y = {h}*z_i = {redondear(k1y)}; k1z = {h}*f({redondear(t)}, {redondear(y)}, {redondear(z)}) = {redondear(k1z)}.",
                    f"k2y = {h}*(z_i+k1z/2) = {redondear(k2y)}; k2z = {h}*f({redondear(t + h / 2)}, {redondear(y + k1y / 2)}, {redondear(z + k1z / 2)}) = {redondear(k2z)}.",
                    f"k3y = {h}*(z_i+k2z/2) = {redondear(k3y)}; k3z = {h}*f({redondear(t + h / 2)}, {redondear(y + k2y / 2)}, {redondear(z + k2z / 2)}) = {redondear(k3z)}.",
                    f"k4y = {h}*(z_i+k3z) = {redondear(k4y)}; k4z = {h}*f({redondear(t + h)}, {redondear(y + k3y)}, {redondear(z + k3z)}) = {redondear(k4z)}.",
                    f"y_{i + 1} = {redondear(y_sig)} y z_{i + 1}=y'_{i + 1} = {redondear(z_sig)}.",
                ])
            t, y, z = t + h, y_sig, z_sig

        if n > 20:
            pasos.append("Se omiten del procedimiento escrito las iteraciones restantes para no saturar la pantalla; la tabla conserva todos los valores.")

        return ResultadoMetodo(
            resultado={"x": redondear(t), "y": redondear(y), "z": redondear(z)},
            mensaje=f"Aproximacion final: y({redondear(t)})={redondear(y)}, y'({redondear(t)})={redondear(z)}",
            pasos=pasos,
            tabla=tabla,
        )
