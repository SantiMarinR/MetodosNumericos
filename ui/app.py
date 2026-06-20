import unicodedata

import numpy as np
import sympy as sp
import customtkinter as ctk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.registro import obtener_metodos


# =========================================================
# ORDEN Y AGRUPACION QUE SE VERA EN LA PANTALLA PRINCIPAL
# =========================================================

CATEGORIAS_UI = [
    {
        "titulo": "Punto flotante",
        "descripcion": "Conversiones, errores, redondeo y truncamiento.",
        "metodos": [
            "Punto flotante",
        ],
    },
    {
        "titulo": "Raíces de ecuaciones",
        "descripcion": "Métodos iterativos para encontrar ceros de funciones.",
        "metodos": [
            "Bisección",
            "Falsa Posición",
            "Secante",
            "Newton",
            "Muller",
        ],
    },
    {
        "titulo": "Interpolación",
        "descripcion": "Construcción de polinomios a partir de datos.",
        "metodos": [
            "Lagrange",
            "Diferencias divididas",
            "Neville",
            "Extrapolación",
        ],
    },
    {
        "titulo": "Aproximación",
        "descripcion": "Ajuste de datos, series y modelos aproximados.",
        "metodos": [
            "Mínimos cuadrados",
            "Ajuste logarítmico",
            "Ajuste exponencial",
            "Polinomio de Taylor",
            "Desarrollo en polinomios",
        ],
    },
    {
        "titulo": "Derivación",
        "descripcion": "Derivadas numéricas por fórmulas de diferencias.",
        "metodos": [
            "2 puntos",
            "3 puntos",
            "5 puntos",
            "Extrapolación en derivación",
        ],
    },
    {
        "titulo": "Integración",
        "descripcion": "Integrales simples, compuestas, dobles y cuadraturas.",
        "metodos": [
            "Trapecio simple",
            "Trapecio compuesto",
            "Simpson 1/3 simple",
            "Simpson 1/3 compuesto",
            "Simpson 3/8 simple",
            "Simpson 3/8 compuesto",
            "Legendre simple",
            "Legendre compuesto",
            "Integral doble por Trapecio",
            "Integral doble por Simpson 1/3",
            "Cuadratura adaptativa",
        ],
    },
]


# =========================================================
# ALIAS
# Sirve para que el nombre bonito del botón encuentre
# el nombre real que tiene cada método en su archivo.
# =========================================================

ALIAS_METODOS = {
    "Bisección": "Biseccion",
    "Biseccion": "Biseccion",

    "Falsa Posición": "Falsa posición",
    "Falsa posicion": "Falsa posición",
    "Falsa posición": "Falsa posición",

    "Muller": "Müller",
    "Müller": "Müller",

    "Mínimos cuadrados": "Mínimos cuadrados",
    "Minimos cuadrados": "Mínimos cuadrados",

    "Ajuste logarítmico": "Ajuste logarítmico",
    "Ajuste logaritmico": "Ajuste logarítmico",

    "Diferencias divididas": "Diferencia dividida adelante",
    "Diferencia dividida": "Diferencia dividida adelante",
    "Diferencia dividida adelante": "Diferencia dividida adelante",
    "Diferencia dividida atrás": "Diferencia dividida atrás",
    "Diferencia dividida atras": "Diferencia dividida atrás",

    "2 puntos": "Derivación por 2 puntos",
    "3 puntos": "Derivación por 3 puntos",
    "5 puntos": "Derivación por 5 puntos",

    "Extrapolación en derivación": "Extrapolación en derivación",
    "Extrapolacion en derivacion": "Extrapolación en derivación",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Métodos Numéricos")
        self.geometry("1500x900")
        self.minsize(1250, 780)
        self.configure(fg_color="#171b22")

        try:
            self.state("zoomed")
        except Exception:
            pass
        self.metodos_clases = obtener_metodos()
        self.metodos_por_nombre = self.crear_indice_metodos()

        self.metodo_actual = None
        self.nombre_metodo_ui = ""
        self.entradas = {}

        self.mostrar_inicio()

    # =========================================================
    # UTILIDADES
    # =========================================================

    def normalizar(self, texto):
        texto = str(texto).strip().lower()
        texto = "".join(
            caracter for caracter in unicodedata.normalize("NFD", texto)
            if unicodedata.category(caracter) != "Mn"
        )
        return texto

    def crear_indice_metodos(self):
        indice = {}

        for clase in self.metodos_clases:
            indice[self.normalizar(clase.nombre)] = clase

        return indice

    def obtener_clase_metodo(self, nombre_ui):
        nombre_real = ALIAS_METODOS.get(nombre_ui, nombre_ui)
        return self.metodos_por_nombre.get(self.normalizar(nombre_real))

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def crear_label(self, padre, texto, tamano=14, peso="normal", color="#e8edf7"):
        return ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", tamano, peso),
            text_color=color,
            justify="left",
        )


    # =========================================================
    # RAICES EXACTAS / SIMBOLICAS
    # =========================================================

    def obtener_raices_exactas_texto(self, funcion_texto):
        """
        Intenta obtener raíces exactas de f(x)=0 cuando la función es polinómica.
        Si la función no es polinómica, muestra un aviso porque no siempre existen
        raíces exactas simbólicas para sen, cos, log, exp, etc.
        """
        try:
            x = sp.symbols("x")
            expresion = str(funcion_texto).strip()

            if not expresion:
                return "Raíces exactas: función vacía."

            if hasattr(self.metodo_actual, "preparar_expresion"):
                expresion = self.metodo_actual.preparar_expresion(expresion)
            else:
                expresion = expresion.replace("^", "**")
                expresion = expresion.replace("sen", "sin")
                expresion = expresion.replace("ln", "log")

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

            expresion_simbolica = sp.sympify(expresion, locals=locales)
            expresion_simbolica = sp.nsimplify(expresion_simbolica)

            try:
                polinomio = sp.Poly(expresion_simbolica, x)
            except Exception:
                return "Raíces exactas: no aplica de forma simbólica para esta función."

            raices_con_multiplicidad = sp.roots(polinomio.as_expr(), x)

            if not raices_con_multiplicidad:
                raices_numericas = []
                for raiz in sp.nroots(polinomio.as_expr()):
                    raiz_compleja = complex(raiz)
                    if abs(raiz_compleja.imag) < 1e-9:
                        raices_numericas.append(raiz_compleja.real)

                if not raices_numericas:
                    return "Raíces exactas: no se encontraron raíces reales."

                texto_aprox = ", ".join(f"x ≈ {raiz:.10f}" for raiz in raices_numericas)
                return f"Raíces aproximadas reales: {texto_aprox}"

            partes = []

            for raiz, multiplicidad in raices_con_multiplicidad.items():
                raiz_compleja = complex(sp.N(raiz, 15))

                if abs(raiz_compleja.imag) >= 1e-9:
                    continue

                raiz_exacta = sp.sstr(sp.simplify(raiz))
                raiz_decimal = float(raiz_compleja.real)

                if multiplicidad > 1:
                    partes.append(f"x = {raiz_exacta} ≈ {raiz_decimal:.10f} (mult. {multiplicidad})")
                else:
                    partes.append(f"x = {raiz_exacta} ≈ {raiz_decimal:.10f}")

            if not partes:
                return "Raíces exactas: no se encontraron raíces reales."

            return "Raíces exactas: " + "; ".join(partes)

        except Exception as error:
            return f"Raíces exactas: no se pudieron calcular ({error})."

    def agregar_raices_exactas_a_datos(self, datos, funcion_texto):
        raices = self.obtener_raices_exactas_texto(funcion_texto)
        mensaje_actual = datos.get("mensaje", "")
        datos["mensaje"] = f"{mensaje_actual}\n{raices}"
        datos["raices_exactas"] = raices
        return datos

    # =========================================================
    # PANTALLA PRINCIPAL
    # =========================================================

    def mostrar_inicio(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.grid(row=0, column=0, sticky="nsew", padx=42, pady=28)
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_rowconfigure(2, weight=1)

        encabezado = ctk.CTkFrame(
            contenedor,
            fg_color="#102d52",
            corner_radius=18,
            border_width=1,
            border_color="#224f83",
        )
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        encabezado.grid_columnconfigure(0, weight=1)

        self.crear_label(
            encabezado,
            "PROYECTO SEMESTRAL",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=32, pady=(30, 0), sticky="w")

        self.crear_label(
            encabezado,
            "Métodos Numéricos",
            tamano=44,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=32, pady=(4, 6), sticky="w")

        self.crear_label(
            encabezado,
            "Selecciona una categoría y después el método que quieres resolver.",
            tamano=14,
            color="#d7e6ff",
        ).grid(row=2, column=0, padx=32, pady=(0, 32), sticky="w")

        barra = ctk.CTkFrame(
            contenedor,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#2c3440",
        )
        barra.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        barra.grid_columnconfigure(0, weight=1)

        self.crear_label(
            barra,
            "INICIO",
            tamano=10,
            peso="bold",
            color="#8ca0bd",
        ).grid(row=0, column=0, padx=22, pady=(14, 0), sticky="w")

        self.crear_label(
            barra,
            "¿Qué quieres hacer?",
            tamano=18,
            peso="bold",
            color="#f1f5ff",
        ).grid(row=1, column=0, padx=22, pady=(0, 16), sticky="w")

        zona_tarjetas = ctk.CTkScrollableFrame(
            contenedor,
            fg_color="transparent",
            corner_radius=0,
        )
        zona_tarjetas.grid(row=2, column=0, sticky="nsew")

        for columna in range(3):
            zona_tarjetas.grid_columnconfigure(columna, weight=1, uniform="tarjetas")

        for indice, categoria in enumerate(CATEGORIAS_UI):
            fila = indice // 3
            columna = indice % 3
            self.crear_tarjeta_categoria(zona_tarjetas, categoria, fila, columna)

    def crear_tarjeta_categoria(self, padre, categoria, fila, columna):
        tarjeta = ctk.CTkFrame(
            padre,
            fg_color="#101216",
            corner_radius=14,
            border_width=1,
            border_color="#303846",
        )
        tarjeta.grid(row=fila, column=columna, padx=8, pady=8, sticky="nsew")
        tarjeta.grid_columnconfigure(0, weight=1)

        self.crear_label(
            tarjeta,
            categoria["titulo"],
            tamano=16,
            peso="bold",
            color="#f1f5ff",
        ).grid(row=0, column=0, padx=18, pady=(18, 4), sticky="w")

        self.crear_label(
            tarjeta,
            categoria["descripcion"],
            tamano=12,
            color="#9fb0c7",
        ).grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")

        for i, nombre_metodo in enumerate(categoria["metodos"], start=2):
            boton = ctk.CTkButton(
                tarjeta,
                text=nombre_metodo,
                height=36,
                corner_radius=8,
                fg_color="#1a1f2b",
                hover_color="#123b6d",
                border_width=1,
                border_color="#343c4c",
                text_color="#dce7ff",
                font=("Arial", 13, "bold"),
                command=lambda metodo=nombre_metodo: self.abrir_metodo(metodo),
            )
            boton.grid(row=i, column=0, padx=18, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(tarjeta, text="", height=6).grid(
            row=len(categoria["metodos"]) + 3,
            column=0,
            pady=(0, 8),
        )

    # =========================================================
    # PANTALLA DE CADA METODO
    # =========================================================

    def abrir_metodo(self, nombre_metodo):
        clase = self.obtener_clase_metodo(nombre_metodo)

        if clase is None:
            self.mostrar_error_metodo(nombre_metodo)
            return

        self.metodo_actual = clase()
        self.nombre_metodo_ui = nombre_metodo

        if self.normalizar(nombre_metodo) == self.normalizar("Punto flotante"):
            self.mostrar_punto_flotante()
            return

        if self.normalizar(nombre_metodo) == self.normalizar("Bisección") or self.normalizar(nombre_metodo) == self.normalizar("Biseccion"):
            self.mostrar_biseccion()
            return

        if (
            self.normalizar(nombre_metodo) == self.normalizar("Falsa Posición")
            or self.normalizar(nombre_metodo) == self.normalizar("Falsa posicion")
            or self.normalizar(nombre_metodo) == self.normalizar("Falsa posición")
        ):
            self.mostrar_falsa_posicion()
            return

        if self.normalizar(nombre_metodo) == self.normalizar("Secante"):
            self.mostrar_secante()
            return

        if self.normalizar(nombre_metodo) == self.normalizar("Newton"):
            self.mostrar_newton()
            return

        if self.normalizar(nombre_metodo) == self.normalizar("Muller") or self.normalizar(nombre_metodo) == self.normalizar("Müller"):
            self.mostrar_muller()
            return

        if self.normalizar(nombre_metodo) == self.normalizar("Lagrange"):
            self.mostrar_lagrange()
            return

        if self.normalizar(nombre_metodo) == self.normalizar("Neville"):
            self.mostrar_neville()
            return

        if (
            self.normalizar(nombre_metodo) == self.normalizar("Diferencias divididas")
            or self.normalizar(nombre_metodo) == self.normalizar("Diferencia dividida")
            or self.normalizar(nombre_metodo) == self.normalizar("Diferencia dividida adelante")
            or self.normalizar(nombre_metodo) == self.normalizar("Diferencia dividida atrás")
            or self.normalizar(nombre_metodo) == self.normalizar("Diferencia dividida atras")
        ):
            self.mostrar_diferencias_divididas()
            return

        self.mostrar_pantalla_metodo()

    def mostrar_error_metodo(self, nombre_metodo):
        self.limpiar_pantalla()

        frame = ctk.CTkFrame(self, fg_color="#101216", corner_radius=16)
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.crear_label(
            frame,
            "Método no encontrado",
            tamano=28,
            peso="bold",
            color="#ffffff",
        ).pack(padx=30, pady=(35, 8), anchor="w")

        self.crear_label(
            frame,
            f"No se encontró una clase registrada para: {nombre_metodo}",
            tamano=15,
            color="#cbd5e1",
        ).pack(padx=30, pady=(0, 20), anchor="w")

        ctk.CTkButton(
            frame,
            text="Regresar al inicio",
            command=self.mostrar_inicio,
            height=38,
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).pack(padx=30, pady=10, anchor="w")

    def mostrar_pantalla_metodo(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            self.metodo_actual.nombre,
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=32, pady=28, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_formulario = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_formulario.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        panel_formulario.grid_columnconfigure(0, weight=1)
        panel_formulario.grid_rowconfigure(3, weight=1)

        self.crear_label(
            panel_formulario,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=24, pady=(24, 0), sticky="w")

        self.crear_label(
            panel_formulario,
            self.metodo_actual.descripcion,
            tamano=14,
            color="#cbd5e1",
        ).grid(row=1, column=0, padx=24, pady=(6, 16), sticky="w")

        self.frame_formulario = ctk.CTkScrollableFrame(
            panel_formulario,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.frame_formulario.grid(row=3, column=0, padx=24, pady=(0, 18), sticky="nsew")
        self.frame_formulario.grid_columnconfigure(0, weight=1)

        self.construir_formulario()

        self.boton_calcular = ctk.CTkButton(
            panel_formulario,
            text="Calcular",
            command=self.calcular,
            height=42,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        )
        self.boton_calcular.grid(row=4, column=0, padx=24, pady=(0, 24), sticky="ew")

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(12, 0), sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.crear_label(
            panel_resultado,
            "RESULTADO",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=24, pady=(24, 0), sticky="w")

        self.crear_label(
            panel_resultado,
            "Procedimiento, tabla y resultado final.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=1, column=0, padx=24, pady=(6, 16), sticky="w")

        self.salida_texto = ctk.CTkTextbox(
            panel_resultado,
            wrap="word",
            corner_radius=12,
            fg_color="#151a22",
            border_width=1,
            border_color="#2a3342",
            text_color="#e8edf7",
            font=("Consolas", 13),
        )
        self.salida_texto.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self.salida_texto.insert("1.0", "Llena los datos y presiona Calcular.")

    def construir_formulario(self):
        for widget in self.frame_formulario.winfo_children():
            widget.destroy()

        self.entradas = {}

        if not self.metodo_actual.parametros:
            aviso = ctk.CTkLabel(
                self.frame_formulario,
                text=(
                    "Este método todavía no tiene parámetros definidos.\n\n"
                    "Cuando tu equipo programe este archivo, agreguen aquí los campos "
                    "en la variable parametros."
                ),
                font=("Arial", 14),
                text_color="#e5c07b",
                justify="left",
                wraplength=470,
            )
            aviso.grid(row=0, column=0, padx=18, pady=18, sticky="w")
            return

        for i, parametro in enumerate(self.metodo_actual.parametros):
            label = ctk.CTkLabel(
                self.frame_formulario,
                text=parametro.get("label", parametro.get("nombre", "Parámetro")),
                font=("Arial", 14, "bold"),
                text_color="#f1f5ff",
                justify="left",
            )
            label.grid(row=i * 2, column=0, padx=18, pady=(14, 4), sticky="w")

            entrada = ctk.CTkEntry(
                self.frame_formulario,
                placeholder_text=parametro.get("placeholder", ""),
                height=38,
                corner_radius=9,
                fg_color="#0f141b",
                border_color="#344054",
                text_color="#ffffff",
                font=("Arial", 14),
            )
            entrada.grid(row=i * 2 + 1, column=0, padx=18, pady=(0, 8), sticky="ew")

            self.entradas[parametro["nombre"]] = entrada
    # =========================================================
    # PANTALLA ESPECIAL: PUNTO FLOTANTE
    # =========================================================

    def mostrar_punto_flotante(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Punto flotante",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=32, pady=28, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabs = ctk.CTkTabview(
            cuerpo,
            fg_color="#101216",
            segmented_button_fg_color="#151a22",
            segmented_button_selected_color="#1f6feb",
            segmented_button_selected_hover_color="#1959bd",
            segmented_button_unselected_color="#1a1f2b",
            segmented_button_unselected_hover_color="#243044",
            text_color="#ffffff",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        tabs.grid(row=0, column=0, sticky="nsew")

        tabs.add("Decimal a N.P.F.")
        tabs.add("Bits a valor decimal")

        self.construir_opcion_decimal_pf(tabs.tab("Decimal a N.P.F."))
        self.construir_opcion_bits_pf(tabs.tab("Bits a valor decimal"))

    def crear_input_pf(self, padre, fila, texto, placeholder=""):
        etiqueta = ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
            justify="left",
        )
        etiqueta.grid(row=fila, column=0, padx=18, pady=(12, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=36,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 13),
        )
        entrada.grid(row=fila + 1, column=0, padx=18, pady=(0, 4), sticky="ew")
        return entrada

    def construir_opcion_decimal_pf(self, padre):
        padre.grid_columnconfigure(0, weight=1)
        padre.grid_columnconfigure(1, weight=1)
        padre.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkScrollableFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        panel.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        self.crear_label(
            panel,
            "OPCIÓN 1",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=18, pady=(18, 0), sticky="w")

        self.crear_label(
            panel,
            "Datos para representar un número en N.P.F.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=18, pady=(4, 8), sticky="w")

        self.pf_numero = self.crear_input_pf(panel, 2, "Número decimal a representar", "Ejemplo: 11.15625")
        self.pf_total_bits = self.crear_input_pf(panel, 4, "Bits considerados para la representación", "Ejemplo: 16")
        self.pf_bits_signo = self.crear_input_pf(panel, 6, "Bits para signo", "Ejemplo: 1")
        self.pf_bits_exponente = self.crear_input_pf(panel, 8, "Bits para exponente / característica", "Ejemplo: 5")
        self.pf_bits_mantisa = self.crear_input_pf(panel, 10, "Bits para parte decimal / mantisa", "Ejemplo: 10")

        ctk.CTkLabel(
            panel,
            text="Tipo de representación",
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=12, column=0, padx=18, pady=(12, 4), sticky="w")

        self.pf_modo = ctk.CTkOptionMenu(
            panel,
            values=["IEEE 754 / normalizada", "Representación simple"],
            height=36,
            fg_color="#1a1f2b",
            button_color="#1f6feb",
            button_hover_color="#1959bd",
            text_color="#ffffff",
        )
        self.pf_modo.grid(row=13, column=0, padx=18, pady=(0, 14), sticky="ew")
        self.pf_modo.set("IEEE 754 / normalizada")

        ctk.CTkButton(
            panel,
            text="Representar número",
            command=self.calcular_decimal_pf,
            height=42,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=14, column=0, padx=18, pady=(4, 22), sticky="ew")

        self.pf_resultado_decimal = ctk.CTkScrollableFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        self.pf_resultado_decimal.grid(row=0, column=1, padx=(8, 12), pady=12, sticky="nsew")
        self.pf_resultado_decimal.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.pf_resultado_decimal,
            "Aquí aparecerá la representación visual.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def construir_opcion_bits_pf(self, padre):
        padre.grid_columnconfigure(0, weight=1)
        padre.grid_columnconfigure(1, weight=1)
        padre.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkScrollableFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        panel.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        self.crear_label(
            panel,
            "OPCIÓN 2",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=18, pady=(18, 0), sticky="w")

        self.crear_label(
            panel,
            "Tabla de bits para obtener el valor decimal.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=18, pady=(4, 8), sticky="w")

        self.pf2_total_bits = self.crear_input_pf(panel, 2, "Bits considerados para la representación", "Ejemplo: 16")
        self.pf2_bits_signo = self.crear_input_pf(panel, 4, "Bits para signo", "Ejemplo: 1")
        self.pf2_bits_exponente = self.crear_input_pf(panel, 6, "Bits para exponente / característica", "Ejemplo: 5")
        self.pf2_bits_mantisa = self.crear_input_pf(panel, 8, "Bits para parte decimal / mantisa", "Ejemplo: 10")

        ctk.CTkLabel(
            panel,
            text="Tipo de representación",
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=10, column=0, padx=18, pady=(12, 4), sticky="w")

        self.pf2_modo = ctk.CTkOptionMenu(
            panel,
            values=["IEEE 754 / normalizada", "Representación simple"],
            height=36,
            fg_color="#1a1f2b",
            button_color="#1f6feb",
            button_hover_color="#1959bd",
            text_color="#ffffff",
        )
        self.pf2_modo.grid(row=11, column=0, padx=18, pady=(0, 14), sticky="ew")
        self.pf2_modo.set("IEEE 754 / normalizada")

        ctk.CTkButton(
            panel,
            text="Crear tabla de bits",
            command=self.crear_tabla_bits_pf,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=12, column=0, padx=18, pady=(4, 14), sticky="ew")

        self.pf_tabla_bits = ctk.CTkScrollableFrame(
            panel,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
            height=150,
        )
        self.pf_tabla_bits.grid(row=13, column=0, padx=18, pady=(0, 14), sticky="ew")

        ctk.CTkButton(
            panel,
            text="Interpretar bits",
            command=self.calcular_bits_pf,
            height=42,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=14, column=0, padx=18, pady=(4, 22), sticky="ew")

        self.pf_resultado_bits = ctk.CTkScrollableFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        self.pf_resultado_bits.grid(row=0, column=1, padx=(8, 12), pady=12, sticky="nsew")
        self.pf_resultado_bits.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.pf_resultado_bits,
            "Crea la tabla, llena los bits y presiona Interpretar bits.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.pf_bits_entries = []

    def limitar_bit_pf(self, entrada):
        valor = entrada.get()
        nuevo = "".join(caracter for caracter in valor if caracter in "01")[:1]
        if valor != nuevo:
            entrada.delete(0, "end")
            entrada.insert(0, nuevo)

    def crear_tabla_bits_pf(self):
        for widget in self.pf_tabla_bits.winfo_children():
            widget.destroy()

        self.pf_bits_entries = []

        try:
            total = int(self.pf2_total_bits.get())
            signo = int(self.pf2_bits_signo.get())
            exponente = int(self.pf2_bits_exponente.get())
            mantisa = int(self.pf2_bits_mantisa.get())

            self.metodo_actual.validar_configuracion(total, signo, exponente, mantisa)

            if total > 64:
                raise ValueError("Para que la tabla se vea bien, usa máximo 64 bits.")

            for columna in range(total):
                if columna < signo:
                    color = "#ef4444"
                    texto = "S"
                elif columna < signo + exponente:
                    color = "#f28c28"
                    texto = "E"
                else:
                    color = "#159a73"
                    texto = "M"

                ctk.CTkLabel(
                    self.pf_tabla_bits,
                    text=texto,
                    width=34,
                    height=24,
                    fg_color=color,
                    corner_radius=7,
                    text_color="#ffffff",
                    font=("Arial", 11, "bold"),
                ).grid(row=0, column=columna, padx=3, pady=(12, 4))

                entrada = ctk.CTkEntry(
                    self.pf_tabla_bits,
                    width=34,
                    height=34,
                    justify="center",
                    fg_color="#0f141b",
                    border_color=color,
                    text_color="#ffffff",
                    font=("Arial", 14, "bold"),
                )
                entrada.grid(row=1, column=columna, padx=3, pady=(0, 12))
                entrada.bind("<KeyRelease>", lambda evento, e=entrada: self.limitar_bit_pf(e))
                self.pf_bits_entries.append(entrada)

        except Exception as error:
            ctk.CTkLabel(
                self.pf_tabla_bits,
                text=f"Error: {error}",
                text_color="#fca5a5",
                font=("Arial", 13, "bold"),
                wraplength=520,
                justify="left",
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

    def calcular_decimal_pf(self):
        try:
            datos = self.metodo_actual.decimal_a_npf(
                numero=self.pf_numero.get(),
                total_bits=self.pf_total_bits.get(),
                bits_signo=self.pf_bits_signo.get(),
                bits_exponente=self.pf_bits_exponente.get(),
                bits_mantisa=self.pf_bits_mantisa.get(),
                modo=self.pf_modo.get(),
            )
            self.mostrar_resultado_pf(self.pf_resultado_decimal, datos)
        except Exception as error:
            self.mostrar_error_pf(self.pf_resultado_decimal, error)

    def calcular_bits_pf(self):
        try:
            if not self.pf_bits_entries:
                raise ValueError("Primero crea la tabla de bits.")

            bits = [entrada.get() for entrada in self.pf_bits_entries]

            if any(bit == "" for bit in bits):
                raise ValueError("Llena todos los bits antes de interpretar la representación.")

            datos = self.metodo_actual.npf_a_decimal(
                bits=bits,
                total_bits=self.pf2_total_bits.get(),
                bits_signo=self.pf2_bits_signo.get(),
                bits_exponente=self.pf2_bits_exponente.get(),
                bits_mantisa=self.pf2_bits_mantisa.get(),
                modo=self.pf2_modo.get(),
            )
            self.mostrar_resultado_pf(self.pf_resultado_bits, datos)
        except Exception as error:
            self.mostrar_error_pf(self.pf_resultado_bits, error)

    def mostrar_error_pf(self, padre, error):
        for widget in padre.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            padre,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            padre,
            text=str(error),
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=540,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")

    def mostrar_resultado_pf(self, padre, datos):
        for widget in padre.winfo_children():
            widget.destroy()

        padre.grid_columnconfigure(0, weight=1)

        self.crear_label(
            padre,
            "Procedimiento",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 10), sticky="w")

        bits_frame = ctk.CTkFrame(padre, fg_color="transparent")
        bits_frame.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="w")

        colores = []
        colores += ["#ef4444"] * len(datos["bits_signo"])
        colores += ["#f28c28"] * len(datos["bits_exponente"])
        colores += ["#159a73"] * len(datos["bits_mantisa"])

        for i, bit in enumerate(datos["bits"]):
            ctk.CTkLabel(
                bits_frame,
                text=bit,
                width=38,
                height=38,
                fg_color=colores[i],
                corner_radius=9,
                text_color="#ffffff",
                font=("Arial", 15, "bold"),
            ).grid(row=0, column=i, padx=4, pady=4)

        leyenda = ctk.CTkFrame(padre, fg_color="transparent")
        leyenda.grid(row=2, column=0, padx=18, pady=(0, 14), sticky="w")

        elementos = [
            ("signo", "#ef4444"),
            ("exponente", "#f28c28"),
            ("mantisa", "#159a73"),
        ]

        for i, (texto, color) in enumerate(elementos):
            ctk.CTkLabel(
                leyenda,
                text="●",
                text_color=color,
                font=("Arial", 16, "bold"),
            ).grid(row=0, column=i * 2, padx=(0, 5), sticky="w")

            ctk.CTkLabel(
                leyenda,
                text=texto,
                text_color="#bcd0ee",
                font=("Arial", 13),
            ).grid(row=0, column=i * 2 + 1, padx=(0, 14), sticky="w")

        tarjeta = ctk.CTkFrame(
            padre,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=3, column=0, padx=18, pady=(0, 14), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Valor decimal",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=18, pady=(14, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["formula"],
            font=("Arial", 15, "bold"),
            text_color="#ffffff",
        ).grid(row=1, column=0, padx=18, pady=(0, 8), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"{datos['valor_decimal']:.10f}",
            font=("Arial", 24, "bold"),
            text_color="#9fffe4",
        ).grid(row=2, column=0, padx=18, pady=(0, 16), sticky="w")

        resumen = ctk.CTkTextbox(
            padre,
            height=210,
            wrap="word",
            corner_radius=12,
            fg_color="#101216",
            border_width=1,
            border_color="#303846",
            text_color="#e8edf7",
            font=("Consolas", 13),
        )
        resumen.grid(row=4, column=0, padx=18, pady=(0, 18), sticky="ew")

        texto = ""
        texto += f"Bits completos: {datos['bits_texto']}\n"
        texto += f"Signo: {''.join(datos['bits_signo'])}\n"
        texto += f"Exponente/característica: {''.join(datos['bits_exponente'])}\n"
        texto += f"Mantisa: {''.join(datos['bits_mantisa'])}\n"
        texto += f"Sesgo: {datos['sesgo']}\n"
        texto += f"Exponente real: {datos['exponente_real']}\n\n"
        texto += "Pasos:\n"

        for i, paso in enumerate(datos["pasos"], start=1):
            texto += f"{i}. {paso}\n"

        resumen.insert("1.0", texto)
        resumen.configure(state="disabled")

    # =========================================================
    # PANTALLA ESPECIAL: BISECCION
    # =========================================================

    def mostrar_biseccion(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Bisección",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.bis_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Construye la función, define el intervalo y ejecuta el método.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.bis_funcion = self.crear_input_biseccion(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: x**3 - x - 2"
        )

        self.construir_calculadora_biseccion(panel_entrada, 4)

        datos_intervalo = ctk.CTkFrame(panel_entrada, fg_color="transparent")
        datos_intervalo.grid(row=5, column=0, padx=22, pady=(12, 4), sticky="ew")
        datos_intervalo.grid_columnconfigure(0, weight=1)
        datos_intervalo.grid_columnconfigure(1, weight=1)
        datos_intervalo.grid_columnconfigure(2, weight=1)

        self.bis_a = self.crear_input_biseccion_chico(datos_intervalo, 0, "Límite a", "1")
        self.bis_b = self.crear_input_biseccion_chico(datos_intervalo, 1, "Límite b", "2")
        self.bis_error = self.crear_input_biseccion_chico(datos_intervalo, 2, "Error máximo", "0.001")

        ctk.CTkButton(
            panel_entrada,
            text="Graficar función",
            command=self.graficar_biseccion_desde_formulario,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=6, column=0, padx=22, pady=(12, 8), sticky="ew")

        ctk.CTkButton(
            panel_entrada,
            text="Calcular bisección",
            command=self.calcular_biseccion,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.bis_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.bis_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.bis_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.bis_grafica_frame,
            "Aquí aparecerá la gráfica de f(x) con los puntos a, b y c.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.bis_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.bis_tabla_frame.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.bis_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.bis_tabla_frame,
            "Aquí aparecerá la tabla de iteraciones.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_biseccion(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def crear_input_biseccion_chico(self, padre, columna, texto, placeholder=""):
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.grid(row=0, column=columna, padx=6, pady=0, sticky="ew")
        contenedor.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            contenedor,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=0, column=0, pady=(0, 4), sticky="w")

        entrada = ctk.CTkEntry(
            contenedor,
            placeholder_text=placeholder,
            height=36,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 13),
        )
        entrada.grid(row=1, column=0, sticky="ew")
        return entrada

    def construir_calculadora_biseccion(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_biseccion
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_biseccion
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_biseccion(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_biseccion(self, texto):
        self.bis_funcion.insert("end", texto)
        self.bis_funcion.focus()

    def limpiar_funcion_biseccion(self):
        self.bis_funcion.delete(0, "end")
        self.bis_funcion.focus()

    def borrar_funcion_biseccion(self):
        texto = self.bis_funcion.get()
        self.bis_funcion.delete(0, "end")
        self.bis_funcion.insert(0, texto[:-1])
        self.bis_funcion.focus()

    def limpiar_grafica_biseccion(self):
        for widget in self.bis_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_biseccion(self):
        for widget in self.bis_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_biseccion(self, valor):
        try:
            return f"{float(valor):.6f}"
        except Exception:
            return str(valor)

    def leer_numero_biseccion(self, entrada):
        texto = entrada.get().strip()

        if hasattr(self.metodo_actual, "convertir_numero"):
            return self.metodo_actual.convertir_numero(texto)

        return float(texto)

    def graficar_biseccion_desde_formulario(self):
        try:
            expresion = self.bis_funcion.get()
            a = self.leer_numero_biseccion(self.bis_a)
            b = self.leer_numero_biseccion(self.bis_b)

            _, _, f_numpy = self.metodo_actual.obtener_funciones(expresion)

            self.dibujar_grafica_biseccion(
                funcion_numpy=f_numpy,
                a=a,
                b=b,
                c=None,
            )
        except Exception as error:
            self.mostrar_error_biseccion(str(error))

    def calcular_biseccion(self):
        try:
            datos = self.metodo_actual.calcular_detallado(
                funcion=self.bis_funcion.get(),
                a=self.bis_a.get(),
                b=self.bis_b.get(),
                tolerancia=self.bis_error.get(),
            )
            datos = self.agregar_raices_exactas_a_datos(datos, self.bis_funcion.get())

            self.dibujar_grafica_biseccion(
                funcion_numpy=datos["funcion_numpy"],
                a=datos["a_inicial"],
                b=datos["b_inicial"],
                c=datos["c_final"],
            )

            self.mostrar_tabla_biseccion(datos)

        except Exception as error:
            self.mostrar_error_biseccion(str(error))

    def dibujar_grafica_biseccion(self, funcion_numpy, a, b, c=None):
        self.limpiar_grafica_biseccion()

        a = float(a)
        b = float(b)

        x_izquierda = min(a, b)
        x_derecha = max(a, b)
        ancho = x_derecha - x_izquierda

        if ancho <= 0:
            ancho = 1.0

        # Vista enfocada en el intervalo. 
        # Para intervalos muy pequeños no se abre hasta 0, se mantiene cerca de [a,b].
        margen_x = max(ancho * 0.18, ancho * 0.18)
        x_min = x_izquierda - margen_x
        x_max = x_derecha + margen_x

        xs = np.linspace(x_min, x_max, 900)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys = funcion_numpy(xs)
            except Exception:
                ys = np.array([funcion_numpy(float(valor_x)) for valor_x in xs])

        ys = np.array(ys, dtype=float)

        mascara = np.isfinite(ys)
        xs_validos = xs[mascara]
        ys_validos = ys[mascara]

        if len(xs_validos) == 0:
            self.mostrar_error_biseccion("No se pudo graficar la función en ese intervalo.")
            return

        # Escala de Y robusta para que no se aplaste por valores extremos.
        valores_y = list(ys_validos)

        for punto in [a, b, c]:
            if punto is not None:
                try:
                    valor_y = float(funcion_numpy(float(punto)))
                    if np.isfinite(valor_y):
                        valores_y.append(valor_y)
                except Exception:
                    pass

        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        if len(valores_y) == 0:
            y_min, y_max = -1, 1
        else:
            y_min = float(np.min(valores_y))
            y_max = float(np.max(valores_y))

        if y_min == y_max:
            y_min -= 1
            y_max += 1

        margen_y = abs(y_max - y_min) * 0.20
        y_min -= margen_y
        y_max += margen_y

        figura = Figure(figsize=(7.6, 3.9), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(
            xs_validos,
            ys_validos,
            linewidth=2,
            color="#7cc7ff",
            label="f(x)"
        )

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.75)

        # Solo dibujamos eje y si cae dentro de la vista.
        if x_min <= 0 <= x_max:
            eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        def marcar_punto(x_punto, color, etiqueta):
            try:
                y_punto = float(funcion_numpy(float(x_punto)))

                if not np.isfinite(y_punto):
                    return

                eje.scatter(
                    [x_punto],
                    [y_punto],
                    color=color,
                    s=80,
                    label=etiqueta,
                    zorder=6,
                )

                eje.annotate(
                    etiqueta,
                    (x_punto, y_punto),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    color=color,
                    fontsize=12,
                    fontweight="bold",
                )

                eje.axvline(x_punto, color=color, linewidth=1, alpha=0.35)

            except Exception:
                pass

        marcar_punto(a, "#ef4444", "a")
        marcar_punto(b, "#f28c28", "b")

        if c is not None:
            marcar_punto(float(c), "#22c55e", "c")

        eje.set_xlim(x_min, x_max)
        eje.set_ylim(y_min, y_max)

        # Ticks centrados en el intervalo para que no aparezca la escala desde 0.
        ticks_x = np.linspace(x_min, x_max, 6)
        eje.set_xticks(ticks_x)
        eje.set_xticklabels([f"{valor:.5f}" for valor in ticks_x])

        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Gráfica de la función", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")

            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.bis_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_tabla_biseccion(self, datos):
        self.limpiar_tabla_biseccion()

        self.bis_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.bis_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Raíz aproximada",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"{datos['raiz']:.10f}",
            font=("Arial", 24, "bold"),
            text_color="#9fffe4",
        ).grid(row=1, column=0, padx=16, pady=(0, 6), sticky="w")

        max_iteraciones = datos.get("max_iteraciones_calculadas", len(datos.get("tabla", [])))

        ctk.CTkLabel(
            tarjeta,
            text=f"Máximo de iteraciones calculado: {max_iteraciones}",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=2, column=0, padx=16, pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["mensaje"],
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.bis_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        encabezados = [
            "n",
            "a",
            "b",
            "c=(a+b)/2",
            "f(a)",
            "f(c)",
            "f(b)",
            "Cota error",
        ]

        for columna, texto in enumerate(encabezados):
            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#1f2937",
                corner_radius=6,
                width=95,
                height=30,
            ).grid(row=0, column=columna, padx=3, pady=4, sticky="ew")

        for fila_indice, fila in enumerate(datos["tabla"], start=1):
            valores = [
                fila["n"],
                self.formatear_numero_biseccion(fila["a"]),
                self.formatear_numero_biseccion(fila["b"]),
                self.formatear_numero_biseccion(fila["c"]),
                fila["signo_fa"],
                fila["signo_fc"],
                fila["signo_fb"],
                self.formatear_numero_biseccion(fila["cota_error"]),
            ]

            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    font=("Arial", 12),
                    text_color="#e8edf7",
                    fg_color="#151a22",
                    corner_radius=6,
                    width=95,
                    height=28,
                ).grid(row=fila_indice, column=columna, padx=3, pady=3, sticky="ew")

    def mostrar_error_biseccion(self, mensaje):
        self.limpiar_tabla_biseccion()

        ctk.CTkLabel(
            self.bis_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.bis_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")


    # =========================================================
    # PANTALLA ESPECIAL: FALSA POSICION
    # =========================================================

    def mostrar_falsa_posicion(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Falsa Posición",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.fp_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Construye la función, define el intervalo y ejecuta el método.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.fp_funcion = self.crear_input_falsa_posicion(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: x**3 - x - 2"
        )

        self.construir_calculadora_falsa_posicion(panel_entrada, 4)

        datos_intervalo = ctk.CTkFrame(panel_entrada, fg_color="transparent")
        datos_intervalo.grid(row=5, column=0, padx=22, pady=(12, 4), sticky="ew")
        datos_intervalo.grid_columnconfigure(0, weight=1)
        datos_intervalo.grid_columnconfigure(1, weight=1)
        datos_intervalo.grid_columnconfigure(2, weight=1)

        self.fp_a = self.crear_input_falsa_posicion_chico(datos_intervalo, 0, "Límite a", "1")
        self.fp_b = self.crear_input_falsa_posicion_chico(datos_intervalo, 1, "Límite b", "2")
        self.fp_error = self.crear_input_falsa_posicion_chico(datos_intervalo, 2, "Error máximo", "0.001")

        ctk.CTkButton(
            panel_entrada,
            text="Graficar función",
            command=self.graficar_falsa_posicion_desde_formulario,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=6, column=0, padx=22, pady=(12, 8), sticky="ew")

        ctk.CTkButton(
            panel_entrada,
            text="Calcular falsa posición",
            command=self.calcular_falsa_posicion,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.fp_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.fp_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.fp_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.fp_grafica_frame,
            "Aquí aparecerá la gráfica de f(x) con los puntos a, b y c.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.fp_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.fp_tabla_frame.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.fp_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.fp_tabla_frame,
            "Aquí aparecerá la tabla de iteraciones.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_falsa_posicion(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def crear_input_falsa_posicion_chico(self, padre, columna, texto, placeholder=""):
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.grid(row=0, column=columna, padx=6, pady=0, sticky="ew")
        contenedor.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            contenedor,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=0, column=0, pady=(0, 4), sticky="w")

        entrada = ctk.CTkEntry(
            contenedor,
            placeholder_text=placeholder,
            height=36,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 13),
        )
        entrada.grid(row=1, column=0, sticky="ew")
        return entrada

    def construir_calculadora_falsa_posicion(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_falsa_posicion
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_falsa_posicion
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_falsa_posicion(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_falsa_posicion(self, texto):
        self.fp_funcion.insert("end", texto)
        self.fp_funcion.focus()

    def limpiar_funcion_falsa_posicion(self):
        self.fp_funcion.delete(0, "end")
        self.fp_funcion.focus()

    def borrar_funcion_falsa_posicion(self):
        texto = self.fp_funcion.get()
        self.fp_funcion.delete(0, "end")
        self.fp_funcion.insert(0, texto[:-1])
        self.fp_funcion.focus()

    def limpiar_grafica_falsa_posicion(self):
        for widget in self.fp_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_falsa_posicion(self):
        for widget in self.fp_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_falsa_posicion(self, valor):
        try:
            return f"{float(valor):.6f}"
        except Exception:
            return str(valor)

    def graficar_falsa_posicion_desde_formulario(self):
        try:
            expresion = self.fp_funcion.get()
            a = self.metodo_actual.convertir_numero(self.fp_a.get())
            b = self.metodo_actual.convertir_numero(self.fp_b.get())

            _, _, f_numpy = self.metodo_actual.obtener_funciones(expresion)

            self.dibujar_grafica_falsa_posicion(
                funcion_numpy=f_numpy,
                a=a,
                b=b,
                c=None,
            )
        except Exception as error:
            self.mostrar_error_falsa_posicion(str(error))

    def calcular_falsa_posicion(self):
        try:
            datos = self.metodo_actual.calcular_detallado(
                funcion=self.fp_funcion.get(),
                a=self.fp_a.get(),
                b=self.fp_b.get(),
                tolerancia=self.fp_error.get(),
            )
            datos = self.agregar_raices_exactas_a_datos(datos, self.fp_funcion.get())

            self.dibujar_grafica_falsa_posicion(
                funcion_numpy=datos["funcion_numpy"],
                a=datos["a_inicial"],
                b=datos["b_inicial"],
                c=datos["c_final"],
            )

            self.mostrar_tabla_falsa_posicion(datos)

        except Exception as error:
            self.mostrar_error_falsa_posicion(str(error))

    def dibujar_grafica_falsa_posicion(self, funcion_numpy, a, b, c=None):
        self.limpiar_grafica_falsa_posicion()

        ancho = abs(b - a)

        if ancho == 0:
            ancho = 1

        margen_x = ancho * 0.12

        x_min = a - margen_x
        x_max = b + margen_x

        xs = np.linspace(x_min, x_max, 700)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys = funcion_numpy(xs)
            except Exception:
                ys = np.array([funcion_numpy(float(x)) for x in xs])

        ys = np.array(ys, dtype=float)

        mascara = np.isfinite(ys)
        xs_validos = xs[mascara]
        ys_validos = ys[mascara]

        if len(xs_validos) == 0:
            self.mostrar_error_falsa_posicion("No se pudo graficar la función en ese intervalo.")
            return

        valores_y = list(ys_validos)

        fa = None
        fb = None
        fc = None

        try:
            fa = float(funcion_numpy(a))
            fb = float(funcion_numpy(b))
            valores_y.append(fa)
            valores_y.append(fb)
        except Exception:
            pass

        if c is not None:
            try:
                fc = float(funcion_numpy(c))
                valores_y.append(fc)
            except Exception:
                pass

        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        y_min = np.min(valores_y)
        y_max = np.max(valores_y)

        if y_min == y_max:
            y_min -= 1
            y_max += 1

        margen_y = abs(y_max - y_min) * 0.18
        y_min -= margen_y
        y_max += margen_y

        figura = Figure(figsize=(7.4, 3.8), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(
            xs_validos,
            ys_validos,
            linewidth=2,
            color="#7cc7ff",
            label="f(x)"
        )

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.75)
        eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        if fa is not None and fb is not None:
            eje.scatter([a], [fa], color="#ef4444", s=75, label="a", zorder=5)
            eje.scatter([b], [fb], color="#f28c28", s=75, label="b", zorder=5)

            eje.plot(
                [a, b],
                [fa, fb],
                color="#a78bfa",
                linestyle="--",
                linewidth=1.5,
                label="recta secante"
            )

            eje.annotate(
                "a",
                (a, fa),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#ef4444",
                fontsize=12,
                fontweight="bold",
            )

            eje.annotate(
                "b",
                (b, fb),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#f28c28",
                fontsize=12,
                fontweight="bold",
            )

            eje.axvline(a, color="#ef4444", linewidth=1, alpha=0.35)
            eje.axvline(b, color="#f28c28", linewidth=1, alpha=0.35)

        if c is not None and fc is not None:
            eje.scatter([c], [fc], color="#22c55e", s=85, label="c", zorder=6)

            eje.annotate(
                "c",
                (c, fc),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#22c55e",
                fontsize=12,
                fontweight="bold",
            )

            eje.axvline(c, color="#22c55e", linewidth=1, alpha=0.35)

        eje.set_xlim(x_min, x_max)
        eje.set_ylim(y_min, y_max)

        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Gráfica de la función", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")

            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.fp_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_tabla_falsa_posicion(self, datos):
        self.limpiar_tabla_falsa_posicion()

        self.fp_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.fp_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Raíz aproximada",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"{datos['raiz']:.10f}",
            font=("Arial", 24, "bold"),
            text_color="#9fffe4",
        ).grid(row=1, column=0, padx=16, pady=(0, 6), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"Tope automático de iteraciones: {datos['max_iteraciones_calculadas']}",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=2, column=0, padx=16, pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["mensaje"],
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.fp_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        encabezados = [
            "n",
            "a",
            "b",
            "c",
            "f(a)",
            "f(c)",
            "f(b)",
            "Error",
        ]

        for columna, texto in enumerate(encabezados):
            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#1f2937",
                corner_radius=6,
                width=95,
                height=30,
            ).grid(row=0, column=columna, padx=3, pady=4, sticky="ew")

        for fila_indice, fila in enumerate(datos["tabla"], start=1):
            valores = [
                fila["n"],
                self.formatear_numero_falsa_posicion(fila["a"]),
                self.formatear_numero_falsa_posicion(fila["b"]),
                self.formatear_numero_falsa_posicion(fila["c"]),
                fila["signo_fa"],
                fila["signo_fc"],
                fila["signo_fb"],
                self.formatear_numero_falsa_posicion(fila["error"]),
            ]

            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    font=("Arial", 12),
                    text_color="#e8edf7",
                    fg_color="#151a22",
                    corner_radius=6,
                    width=95,
                    height=28,
                ).grid(row=fila_indice, column=columna, padx=3, pady=3, sticky="ew")

    def mostrar_error_falsa_posicion(self, mensaje):
        self.limpiar_tabla_falsa_posicion()

        ctk.CTkLabel(
            self.fp_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.fp_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")

    # =========================================================
    # PANTALLA ESPECIAL: SECANTE
    # =========================================================

    def mostrar_secante(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Secante",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.sec_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Construye la función, escribe p0 y p1, y ejecuta el método.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.sec_funcion = self.crear_input_secante(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: x**3 - x - 2"
        )

        self.construir_calculadora_secante(panel_entrada, 4)

        datos_intervalo = ctk.CTkFrame(panel_entrada, fg_color="transparent")
        datos_intervalo.grid(row=5, column=0, padx=22, pady=(12, 4), sticky="ew")
        datos_intervalo.grid_columnconfigure(0, weight=1)
        datos_intervalo.grid_columnconfigure(1, weight=1)
        datos_intervalo.grid_columnconfigure(2, weight=1)

        self.sec_p0 = self.crear_input_secante_chico(datos_intervalo, 0, "P0", "0")
        self.sec_p1 = self.crear_input_secante_chico(datos_intervalo, 1, "P0+1", "2")
        self.sec_error = self.crear_input_secante_chico(datos_intervalo, 2, "Error máximo", "0.001")

        ctk.CTkButton(
            panel_entrada,
            text="Graficar función",
            command=self.graficar_secante_desde_formulario,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=6, column=0, padx=22, pady=(12, 8), sticky="ew")

        ctk.CTkButton(
            panel_entrada,
            text="Calcular secante",
            command=self.calcular_secante,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.sec_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.sec_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.sec_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.sec_grafica_frame,
            "Aquí aparecerá la gráfica de f(x) con los puntos P0, P0+1 y la aproximación.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.sec_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.sec_tabla_frame.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.sec_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.sec_tabla_frame,
            "Aquí aparecerá la tabla de iteraciones.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_secante(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def crear_input_secante_chico(self, padre, columna, texto, placeholder=""):
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.grid(row=0, column=columna, padx=6, pady=0, sticky="ew")
        contenedor.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            contenedor,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=0, column=0, pady=(0, 4), sticky="w")

        entrada = ctk.CTkEntry(
            contenedor,
            placeholder_text=placeholder,
            height=36,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 13),
        )
        entrada.grid(row=1, column=0, sticky="ew")
        return entrada

    def construir_calculadora_secante(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_secante
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_secante
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_secante(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_secante(self, texto):
        self.sec_funcion.insert("end", texto)
        self.sec_funcion.focus()

    def limpiar_funcion_secante(self):
        self.sec_funcion.delete(0, "end")
        self.sec_funcion.focus()

    def borrar_funcion_secante(self):
        texto = self.sec_funcion.get()
        self.sec_funcion.delete(0, "end")
        self.sec_funcion.insert(0, texto[:-1])
        self.sec_funcion.focus()

    def limpiar_grafica_secante(self):
        for widget in self.sec_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_secante(self):
        for widget in self.sec_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_secante(self, valor):
        try:
            return f"{float(valor):.6f}"
        except Exception:
            return str(valor)

    def graficar_secante_desde_formulario(self):
        try:
            expresion = self.sec_funcion.get()
            p0 = self.metodo_actual.convertir_numero(self.sec_p0.get())
            p1 = self.metodo_actual.convertir_numero(self.sec_p1.get())

            _, _, f_numpy = self.metodo_actual.obtener_funciones(expresion)

            self.dibujar_grafica_secante(
                funcion_numpy=f_numpy,
                p0=p0,
                p1=p1,
                aprox=None,
            )
        except Exception as error:
            self.mostrar_error_secante(str(error))

    def calcular_secante(self):
        try:
            datos = self.metodo_actual.calcular_detallado(
                funcion=self.sec_funcion.get(),
                p0=self.sec_p0.get(),
                p1=self.sec_p1.get(),
                tolerancia=self.sec_error.get(),
            )
            datos = self.agregar_raices_exactas_a_datos(datos, self.sec_funcion.get())

            self.dibujar_grafica_secante(
                funcion_numpy=datos["funcion_numpy"],
                p0=datos["p0_inicial"],
                p1=datos["p1_inicial"],
                aprox=datos["c_final"],
            )

            self.mostrar_tabla_secante(datos)

        except Exception as error:
            self.mostrar_error_secante(str(error))

    def dibujar_grafica_secante(self, funcion_numpy, p0, p1, aprox=None):
        self.limpiar_grafica_secante()

        puntos_x = [p0, p1]
        if aprox is not None:
            puntos_x.append(aprox)

        x_min_base = min(puntos_x)
        x_max_base = max(puntos_x)
        ancho = abs(x_max_base - x_min_base)

        if ancho == 0:
            ancho = 1

        margen_x = ancho * 0.20
        x_min = x_min_base - margen_x
        x_max = x_max_base + margen_x

        xs = np.linspace(x_min, x_max, 700)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys = funcion_numpy(xs)
            except Exception:
                ys = np.array([funcion_numpy(float(x)) for x in xs])

        ys = np.array(ys, dtype=float)

        mascara = np.isfinite(ys)
        xs_validos = xs[mascara]
        ys_validos = ys[mascara]

        if len(xs_validos) == 0:
            self.mostrar_error_secante("No se pudo graficar la función en ese intervalo.")
            return

        valores_y = list(ys_validos)

        try:
            f_p0 = float(funcion_numpy(p0))
            f_p1 = float(funcion_numpy(p1))
            valores_y.append(f_p0)
            valores_y.append(f_p1)
        except Exception:
            f_p0 = None
            f_p1 = None

        if aprox is not None:
            try:
                f_aprox = float(funcion_numpy(aprox))
                valores_y.append(f_aprox)
            except Exception:
                f_aprox = None
        else:
            f_aprox = None

        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        y_min = np.min(valores_y)
        y_max = np.max(valores_y)

        if y_min == y_max:
            y_min -= 1
            y_max += 1

        margen_y = abs(y_max - y_min) * 0.18
        y_min -= margen_y
        y_max += margen_y

        figura = Figure(figsize=(7.4, 3.8), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(
            xs_validos,
            ys_validos,
            linewidth=2,
            color="#7cc7ff",
            label="f(x)"
        )

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.75)
        eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        if f_p0 is not None and f_p1 is not None:
            eje.scatter([p0], [f_p0], color="#ef4444", s=75, label="P0", zorder=5)
            eje.scatter([p1], [f_p1], color="#f28c28", s=75, label="P0+1", zorder=5)

            eje.plot(
                [p0, p1],
                [f_p0, f_p1],
                color="#a78bfa",
                linestyle="--",
                linewidth=1.6,
                label="recta secante"
            )

            eje.annotate(
                "P0",
                (p0, f_p0),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#ef4444",
                fontsize=12,
                fontweight="bold",
            )

            eje.annotate(
                "P0+1",
                (p1, f_p1),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#f28c28",
                fontsize=12,
                fontweight="bold",
            )

            eje.axvline(p0, color="#ef4444", linewidth=1, alpha=0.35)
            eje.axvline(p1, color="#f28c28", linewidth=1, alpha=0.35)

        if aprox is not None and f_aprox is not None:
            eje.scatter([aprox], [f_aprox], color="#22c55e", s=85, label="Aprox", zorder=6)

            eje.annotate(
                "Aprox",
                (aprox, f_aprox),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#22c55e",
                fontsize=12,
                fontweight="bold",
            )

            eje.axvline(aprox, color="#22c55e", linewidth=1, alpha=0.35)

        eje.set_xlim(x_min, x_max)
        eje.set_ylim(y_min, y_max)

        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Gráfica de la función", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")

            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.sec_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_tabla_secante(self, datos):
        self.limpiar_tabla_secante()

        self.sec_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.sec_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Raíz aproximada",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"{datos['raiz']:.10f}",
            font=("Arial", 24, "bold"),
            text_color="#9fffe4",
        ).grid(row=1, column=0, padx=16, pady=(0, 6), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"Tope automático de iteraciones: {datos['max_iteraciones_calculadas']}",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=2, column=0, padx=16, pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["mensaje"],
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.sec_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        encabezados = [
            "Iteración",
            "Pᵢ",
            "Pᵢ₊₁",
            "Aprox",
            "Error",
        ]

        for columna, texto in enumerate(encabezados):
            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#1f2937",
                corner_radius=6,
                width=120,
                height=30,
            ).grid(row=0, column=columna, padx=3, pady=4, sticky="ew")

        for fila_indice, fila in enumerate(datos["tabla"], start=1):
            valores = [
                fila["n"],
                self.formatear_numero_secante(fila["pi"]),
                self.formatear_numero_secante(fila["pi_mas_1"]),
                self.formatear_numero_secante(fila["aprox"]),
                self.formatear_numero_secante(fila["error"]),
            ]

            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    font=("Arial", 12),
                    text_color="#e8edf7",
                    fg_color="#151a22",
                    corner_radius=6,
                    width=120,
                    height=28,
                ).grid(row=fila_indice, column=columna, padx=3, pady=3, sticky="ew")

    def mostrar_error_secante(self, mensaje):
        self.limpiar_tabla_secante()

        ctk.CTkLabel(
            self.sec_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.sec_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")


    # =========================================================
    # PANTALLA ESPECIAL: NEWTON-RAPHSON
    # =========================================================

    def mostrar_newton(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Newton-Raphson",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(4, weight=1)

        self.newton_resultado_panel = panel_resultado
        self.newton_intervalo_actual = None

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Construye la función, elige un P0 cercano y ejecuta Newton-Raphson.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.newton_funcion = self.crear_input_newton(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: 30*x**3 - 325*x**2 + 1170*x - 1400"
        )

        self.construir_calculadora_newton(panel_entrada, 4)

        ctk.CTkLabel(
            panel_entrada,
            text=(
                "El programa buscará automáticamente intervalos con cambio de signo "
                "usando la función escrita y te mostrará opciones para elegir P0."
            ),
            font=("Arial", 13),
            text_color="#cbd5e1",
            justify="left",
            wraplength=560,
        ).grid(row=5, column=0, padx=22, pady=(12, 8), sticky="w")

        ctk.CTkButton(
            panel_entrada,
            text="Buscar P0 sugeridos automáticamente",
            command=self.buscar_intervalos_newton,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#7c3aed",
            hover_color="#6d28d9",
        ).grid(row=6, column=0, padx=22, pady=(0, 10), sticky="ew")

        self.newton_intervalos_frame = ctk.CTkScrollableFrame(
            panel_entrada,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
            height=150,
        )
        self.newton_intervalos_frame.grid(row=7, column=0, padx=22, pady=(0, 14), sticky="ew")
        self.newton_intervalos_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.newton_intervalos_frame,
            "Escribe la función y presiona el botón morado para generar opciones de P0.",
            tamano=13,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

        datos_newton = ctk.CTkFrame(panel_entrada, fg_color="transparent")
        datos_newton.grid(row=8, column=0, padx=22, pady=(4, 4), sticky="ew")
        datos_newton.grid_columnconfigure(0, weight=1)
        datos_newton.grid_columnconfigure(1, weight=1)

        self.newton_p0 = self.crear_input_newton_chico(datos_newton, 0, "P0 elegido", "Elige uno de arriba o escribe uno")
        self.newton_error = self.crear_input_newton_chico(datos_newton, 1, "Error máximo", "1e-5")

        ctk.CTkButton(
            panel_entrada,
            text="Graficar función",
            command=self.graficar_newton_desde_formulario,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=9, column=0, padx=22, pady=(12, 8), sticky="ew")

        ctk.CTkButton(
            panel_entrada,
            text="Calcular Newton-Raphson",
            command=self.calcular_newton,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=10, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "DERIVADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.newton_derivada_label = ctk.CTkLabel(
            panel_resultado,
            text="Aquí aparecerá f'(x).",
            font=("Arial", 14, "bold"),
            text_color="#ffffff",
            fg_color="#151a22",
            corner_radius=10,
            anchor="w",
            justify="left",
        )
        self.newton_derivada_label.grid(row=1, column=0, padx=22, pady=(8, 12), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=2, column=0, padx=22, pady=(0, 0), sticky="w")

        self.newton_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.newton_grafica_frame.grid(row=3, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.newton_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.newton_grafica_frame,
            "Aquí aparecerá la gráfica de f(x), P0, la tangente y la aproximación.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.newton_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.newton_tabla_frame.grid(row=4, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.newton_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.newton_tabla_frame,
            "Aquí aparecerá la tabla de iteraciones.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_newton(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def crear_input_newton_chico(self, padre, columna, texto, placeholder=""):
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.grid(row=0, column=columna, padx=6, pady=0, sticky="ew")
        contenedor.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            contenedor,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=0, column=0, pady=(0, 4), sticky="w")

        entrada = ctk.CTkEntry(
            contenedor,
            placeholder_text=placeholder,
            height=36,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 13),
        )
        entrada.grid(row=1, column=0, sticky="ew")
        return entrada

    def construir_calculadora_newton(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_newton
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_newton
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_newton(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_newton(self, texto):
        self.newton_funcion.insert("end", texto)
        self.newton_funcion.focus()

    def limpiar_funcion_newton(self):
        self.newton_funcion.delete(0, "end")
        self.newton_funcion.focus()

    def borrar_funcion_newton(self):
        texto = self.newton_funcion.get()
        self.newton_funcion.delete(0, "end")
        self.newton_funcion.insert(0, texto[:-1])
        self.newton_funcion.focus()

    def limpiar_grafica_newton(self):
        for widget in self.newton_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_newton(self):
        for widget in self.newton_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_newton(self, valor):
        try:
            return f"{float(valor):.6f}"
        except Exception:
            return str(valor)

    def buscar_intervalos_newton(self):
        for widget in self.newton_intervalos_frame.winfo_children():
            widget.destroy()

        try:
            funcion = self.newton_funcion.get()

            # Búsqueda automática. Primero revisa una zona común;
            # si no encuentra nada, amplía el rango.
            rangos_busqueda = [
                (-10, 10, 0.5),
                (-50, 50, 1),
                (-100, 100, 2),
            ]

            datos = None
            intervalos = []
            rango_usado = None

            for desde, hasta, paso in rangos_busqueda:
                datos = self.metodo_actual.buscar_intervalos_cambio_signo(
                    funcion=funcion,
                    desde=desde,
                    hasta=hasta,
                    paso=paso,
                )

                intervalos = datos["intervalos"]

                if intervalos:
                    rango_usado = (desde, hasta, paso)
                    break

            if datos is None:
                raise ValueError("No se pudo analizar la función.")

            self.newton_derivada_label.configure(
                text=f"f'(x) = {datos['derivada']}"
            )

            if not intervalos:
                self.crear_label(
                    self.newton_intervalos_frame,
                    "No se encontraron cambios de signo de -100 a 100. Puedes escribir P0 manualmente.",
                    tamano=13,
                    color="#fca5a5",
                ).grid(row=0, column=0, padx=12, pady=12, sticky="w")
                return

            desde, hasta, paso = rango_usado

            self.crear_label(
                self.newton_intervalos_frame,
                f"Cambios de signo encontrados automáticamente en [{desde}, {hasta}] con paso {paso}. Elige un P0:",
                tamano=13,
                color="#cbd5e1",
            ).grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")

            for i, intervalo in enumerate(intervalos, start=1):
                texto_boton = (
                    f"Opción {i}: intervalo [{intervalo['a']:.6f}, {intervalo['b']:.6f}]  "
                    f"→ usar P0 = {intervalo['p0_sugerido']:.6f}"
                )

                boton = ctk.CTkButton(
                    self.newton_intervalos_frame,
                    text=texto_boton,
                    height=34,
                    corner_radius=8,
                    fg_color="#1a1f2b",
                    hover_color="#123b6d",
                    border_width=1,
                    border_color="#343c4c",
                    text_color="#ffffff",
                    font=("Arial", 12, "bold"),
                    command=lambda inter=intervalo: self.usar_intervalo_newton(inter),
                )
                boton.grid(row=i, column=0, padx=12, pady=(8, 0), sticky="ew")

        except Exception as error:
            self.crear_label(
                self.newton_intervalos_frame,
                f"Error: {error}",
                tamano=13,
                color="#fca5a5",
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

    def usar_intervalo_newton(self, intervalo):
        p0 = intervalo["p0_sugerido"]
        self.newton_intervalo_actual = (intervalo["a"], intervalo["b"])

        self.newton_p0.delete(0, "end")
        self.newton_p0.insert(0, f"{p0:.10f}")

    def graficar_newton_desde_formulario(self):
        try:
            (
                expresion,
                derivada,
                f,
                fp,
                f_numpy,
                fp_numpy
            ) = self.metodo_actual.obtener_funciones(self.newton_funcion.get())

            p0 = self.metodo_actual.convertir_numero(self.newton_p0.get())

            self.newton_derivada_label.configure(text=f"f'(x) = {derivada}")

            self.dibujar_grafica_newton(
                funcion_numpy=f_numpy,
                derivada_numpy=fp_numpy,
                p0=p0,
                aprox=None,
            )

        except Exception as error:
            self.mostrar_error_newton(str(error))

    def calcular_newton(self):
        try:
            datos = self.metodo_actual.calcular_detallado(
                funcion=self.newton_funcion.get(),
                p0=self.newton_p0.get(),
                tolerancia=self.newton_error.get(),
            )
            datos = self.agregar_raices_exactas_a_datos(datos, self.newton_funcion.get())

            self.newton_derivada_label.configure(
                text=f"f'(x) = {datos['derivada']}"
            )

            self.dibujar_grafica_newton(
                funcion_numpy=datos["funcion_numpy"],
                derivada_numpy=datos["derivada_numpy"],
                p0=datos["p0_inicial"],
                aprox=datos["raiz"],
            )

            self.mostrar_tabla_newton(datos)

        except Exception as error:
            self.mostrar_error_newton(str(error))

    def dibujar_grafica_newton(self, funcion_numpy, derivada_numpy, p0, aprox=None):
        self.limpiar_grafica_newton()

        try:
            y0 = float(funcion_numpy(p0))
            m = float(derivada_numpy(p0))
        except Exception as error:
            self.mostrar_error_newton(f"No se pudo evaluar P0. Detalle: {error}")
            return

        puntos_x = [p0]

        if aprox is not None:
            puntos_x.append(aprox)

        if self.newton_intervalo_actual is not None:
            puntos_x.extend(list(self.newton_intervalo_actual))

        x_min_base = min(puntos_x)
        x_max_base = max(puntos_x)

        ancho = abs(x_max_base - x_min_base)

        if ancho == 0:
            ancho = 1

        margen_x = ancho * 0.35
        x_ini = x_min_base - margen_x
        x_fin = x_max_base + margen_x

        xs = np.linspace(x_ini, x_fin, 800)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys = funcion_numpy(xs)
            except Exception:
                ys = np.array([funcion_numpy(float(x)) for x in xs])

        ys = np.array(ys, dtype=float)

        mascara = np.isfinite(ys)
        xs_validos = xs[mascara]
        ys_validos = ys[mascara]

        if len(xs_validos) == 0:
            self.mostrar_error_newton("No se pudo graficar la función en ese intervalo.")
            return

        ys_tangente = y0 + m * (xs_validos - p0)

        valores_y = list(ys_validos)
        valores_y.append(y0)
        valores_y.append(0)

        if aprox is not None:
            try:
                valor_aprox = float(funcion_numpy(aprox))
                if np.isfinite(valor_aprox):
                    valores_y.append(valor_aprox)
            except Exception:
                pass

        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        y_min = np.min(valores_y)
        y_max = np.max(valores_y)

        if y_min == y_max:
            y_min -= 1
            y_max += 1

        margen_y = abs(y_max - y_min) * 0.20
        y_min -= margen_y
        y_max += margen_y

        figura = Figure(figsize=(7.4, 3.8), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(xs_validos, ys_validos, linewidth=2, color="#7cc7ff", label="f(x)")
        eje.plot(xs_validos, ys_tangente, linestyle="--", linewidth=1.8, color="#a78bfa", label="tangente")

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.75)

        if x_ini <= 0 <= x_fin:
            eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        eje.scatter([p0], [y0], color="#ef4444", s=75, label="P0", zorder=5)

        eje.annotate(
            "P0",
            (p0, y0),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            color="#ef4444",
            fontsize=12,
            fontweight="bold",
        )

        eje.axvline(p0, color="#ef4444", linewidth=1, alpha=0.30)

        if aprox is not None:
            eje.scatter([aprox], [0], color="#22c55e", s=85, label="Raíz aprox", zorder=6)

            eje.annotate(
                "Raíz",
                (aprox, 0),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#22c55e",
                fontsize=12,
                fontweight="bold",
            )

            eje.axvline(aprox, color="#22c55e", linewidth=1, alpha=0.30)

        eje.set_xlim(x_ini, x_fin)
        eje.set_ylim(y_min, y_max)

        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Newton-Raphson", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")

            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.newton_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_tabla_newton(self, datos):
        self.limpiar_tabla_newton()

        self.newton_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.newton_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Raíz aproximada",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"{datos['raiz']:.10f}",
            font=("Arial", 24, "bold"),
            text_color="#9fffe4",
        ).grid(row=1, column=0, padx=16, pady=(0, 6), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["mensaje"],
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
        ).grid(row=2, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.newton_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        encabezados = [
            "n",
            "Pᵢ",
            "f(Pᵢ)",
            "f'(Pᵢ)",
            "Pᵢ₊₁",
            "Error",
        ]

        for columna, texto in enumerate(encabezados):
            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#1f2937",
                corner_radius=6,
                width=110,
                height=30,
            ).grid(row=0, column=columna, padx=3, pady=4, sticky="ew")

        for fila_indice, fila in enumerate(datos["tabla"], start=1):
            valores = [
                fila["n"],
                self.formatear_numero_newton(fila["pi"]),
                self.formatear_numero_newton(fila["fpi"]),
                self.formatear_numero_newton(fila["fppi"]),
                self.formatear_numero_newton(fila["p_siguiente"]),
                self.formatear_numero_newton(fila["error"]),
            ]

            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    font=("Arial", 12),
                    text_color="#e8edf7",
                    fg_color="#151a22",
                    corner_radius=6,
                    width=110,
                    height=28,
                ).grid(row=fila_indice, column=columna, padx=3, pady=3, sticky="ew")

    def mostrar_error_newton(self, mensaje):
        self.limpiar_tabla_newton()

        ctk.CTkLabel(
            self.newton_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.newton_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")


    # =========================================================
    # PANTALLA ESPECIAL: MÜLLER
    # =========================================================

    def mostrar_muller(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Müller",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.muller_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Construye la función, escribe P0, P1 y P2, y ejecuta el método.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.muller_funcion = self.crear_input_muller(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: x**3 - x - 2"
        )

        self.construir_calculadora_muller(panel_entrada, 4)

        datos_intervalo = ctk.CTkFrame(panel_entrada, fg_color="transparent")
        datos_intervalo.grid(row=5, column=0, padx=22, pady=(12, 4), sticky="ew")
        datos_intervalo.grid_columnconfigure(0, weight=1)
        datos_intervalo.grid_columnconfigure(1, weight=1)
        datos_intervalo.grid_columnconfigure(2, weight=1)
        datos_intervalo.grid_columnconfigure(3, weight=1)

        self.muller_p0 = self.crear_input_muller_chico(datos_intervalo, 0, "P0", "0")
        self.muller_p1 = self.crear_input_muller_chico(datos_intervalo, 1, "P1", "1")
        self.muller_p2 = self.crear_input_muller_chico(datos_intervalo, 2, "P2", "2")
        self.muller_error = self.crear_input_muller_chico(datos_intervalo, 3, "Error máximo", "1e-5")

        ctk.CTkButton(
            panel_entrada,
            text="Graficar función",
            command=self.graficar_muller_desde_formulario,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=6, column=0, padx=22, pady=(12, 8), sticky="ew")

        ctk.CTkButton(
            panel_entrada,
            text="Calcular Müller",
            command=self.calcular_muller,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.muller_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.muller_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.muller_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.muller_grafica_frame,
            "Aquí aparecerá la gráfica de f(x), los puntos P0, P1, P2 y la aproximación.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.muller_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.muller_tabla_frame.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.muller_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.muller_tabla_frame,
            "Aquí aparecerá la tabla de iteraciones.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_muller(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def crear_input_muller_chico(self, padre, columna, texto, placeholder=""):
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.grid(row=0, column=columna, padx=6, pady=0, sticky="ew")
        contenedor.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            contenedor,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=0, column=0, pady=(0, 4), sticky="w")

        entrada = ctk.CTkEntry(
            contenedor,
            placeholder_text=placeholder,
            height=36,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 13),
        )
        entrada.grid(row=1, column=0, sticky="ew")
        return entrada

    def construir_calculadora_muller(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_muller
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_muller
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_muller(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_muller(self, texto):
        self.muller_funcion.insert("end", texto)
        self.muller_funcion.focus()

    def limpiar_funcion_muller(self):
        self.muller_funcion.delete(0, "end")
        self.muller_funcion.focus()

    def borrar_funcion_muller(self):
        texto = self.muller_funcion.get()
        self.muller_funcion.delete(0, "end")
        self.muller_funcion.insert(0, texto[:-1])
        self.muller_funcion.focus()

    def limpiar_grafica_muller(self):
        for widget in self.muller_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_muller(self):
        for widget in self.muller_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_muller(self, valor):
        try:
            if hasattr(self.metodo_actual, "formatear_complejo"):
                return self.metodo_actual.formatear_complejo(valor, 6)
            return f"{float(valor):.6f}"
        except Exception:
            return str(valor)

    def muller_a_real_grafica(self, valor):
        valor = complex(valor)
        if abs(valor.imag) < 1e-8:
            return float(valor.real)
        return None

    def graficar_muller_desde_formulario(self):
        try:
            expresion = self.muller_funcion.get()
            p0 = self.metodo_actual.convertir_numero(self.muller_p0.get())
            p1 = self.metodo_actual.convertir_numero(self.muller_p1.get())
            p2 = self.metodo_actual.convertir_numero(self.muller_p2.get())

            _, f_numpy = self.metodo_actual.obtener_funciones(expresion)

            self.dibujar_grafica_muller(
                funcion_numpy=f_numpy,
                p0=p0,
                p1=p1,
                p2=p2,
                aprox=None,
            )
        except Exception as error:
            self.mostrar_error_muller(str(error))

    def calcular_muller(self):
        try:
            datos = self.metodo_actual.calcular_detallado(
                funcion=self.muller_funcion.get(),
                p0=self.muller_p0.get(),
                p1=self.muller_p1.get(),
                p2=self.muller_p2.get(),
                tolerancia=self.muller_error.get(),
            )

            datos = self.agregar_raices_exactas_a_datos(datos, self.muller_funcion.get())

            self.dibujar_grafica_muller(
                funcion_numpy=datos["funcion_numpy"],
                p0=datos["p0_inicial"],
                p1=datos["p1_inicial"],
                p2=datos["p2_inicial"],
                aprox=datos["c_final"],
            )

            self.mostrar_tabla_muller(datos)

        except Exception as error:
            self.mostrar_error_muller(str(error))

    def dibujar_grafica_muller(self, funcion_numpy, p0, p1, p2, aprox=None):
        self.limpiar_grafica_muller()

        puntos_reales = []

        for punto in [p0, p1, p2, aprox]:
            if punto is not None:
                valor_real = self.muller_a_real_grafica(punto)
                if valor_real is not None:
                    puntos_reales.append(valor_real)

        if not puntos_reales:
            self.mostrar_error_muller("La aproximación es compleja; no se puede representar completa en la gráfica real.")
            return

        x_min_base = min(puntos_reales)
        x_max_base = max(puntos_reales)
        ancho = abs(x_max_base - x_min_base)

        if ancho == 0:
            ancho = 1

        margen_x = ancho * 0.35
        x_min = x_min_base - margen_x
        x_max = x_max_base + margen_x

        xs = np.linspace(x_min, x_max, 900)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys = funcion_numpy(xs)
            except Exception:
                ys = np.array([funcion_numpy(float(x)) for x in xs])

        ys = np.array(ys, dtype=complex)

        mascara = np.isfinite(ys.real) & np.isfinite(ys.imag) & (np.abs(ys.imag) < 1e-8)
        xs_validos = xs[mascara]
        ys_validos = ys.real[mascara]

        if len(xs_validos) == 0:
            self.mostrar_error_muller("No se pudo graficar la función en ese intervalo.")
            return

        valores_y = list(ys_validos)

        puntos_info = []
        for punto, etiqueta, color in [
            (p0, "P0", "#ef4444"),
            (p1, "P1", "#f28c28"),
            (p2, "P2", "#eab308"),
            (aprox, "Aprox", "#22c55e"),
        ]:
            x_real = None if punto is None else self.muller_a_real_grafica(punto)
            if x_real is None:
                continue

            try:
                y_punto = complex(funcion_numpy(x_real))
                if abs(y_punto.imag) < 1e-8 and np.isfinite(y_punto.real):
                    puntos_info.append((x_real, float(y_punto.real), etiqueta, color))
                    valores_y.append(float(y_punto.real))
            except Exception:
                pass

        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        y_min = np.min(valores_y)
        y_max = np.max(valores_y)

        if y_min == y_max:
            y_min -= 1
            y_max += 1

        margen_y = abs(y_max - y_min) * 0.18
        y_min -= margen_y
        y_max += margen_y

        figura = Figure(figsize=(7.4, 3.8), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(
            xs_validos,
            ys_validos,
            linewidth=2,
            color="#7cc7ff",
            label="f(x)"
        )

        # Parábola interpolante que usa Müller en la primera iteración.
        try:
            puntos_iniciales = []
            for punto in [p0, p1, p2]:
                x_real = self.muller_a_real_grafica(punto)
                if x_real is None:
                    raise ValueError()
                y_real = complex(funcion_numpy(x_real))
                if abs(y_real.imag) >= 1e-8:
                    raise ValueError()
                puntos_iniciales.append((x_real, float(y_real.real)))

            xs_parabola = np.array([p[0] for p in puntos_iniciales], dtype=float)
            ys_parabola = np.array([p[1] for p in puntos_iniciales], dtype=float)

            if len(set(xs_parabola)) == 3:
                coeficientes = np.polyfit(xs_parabola, ys_parabola, 2)
                y_parabola = np.polyval(coeficientes, xs_validos)
                eje.plot(
                    xs_validos,
                    y_parabola,
                    color="#a78bfa",
                    linestyle="--",
                    linewidth=1.5,
                    label="parábola de Müller"
                )
        except Exception:
            pass

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.75)
        if x_min <= 0 <= x_max:
            eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        for x_punto, y_punto, etiqueta, color in puntos_info:
            eje.scatter([x_punto], [y_punto], color=color, s=80, label=etiqueta, zorder=6)

            eje.annotate(
                etiqueta,
                (x_punto, y_punto),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color=color,
                fontsize=12,
                fontweight="bold",
            )

            eje.axvline(x_punto, color=color, linewidth=1, alpha=0.35)

        eje.set_xlim(x_min, x_max)
        eje.set_ylim(y_min, y_max)

        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Método de Müller", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")

            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.muller_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_tabla_muller(self, datos):
        self.limpiar_tabla_muller()

        self.muller_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.muller_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Raíz aproximada",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos.get("raiz_texto", str(datos["raiz"])),
            font=("Arial", 24, "bold"),
            text_color="#9fffe4",
        ).grid(row=1, column=0, padx=16, pady=(0, 6), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["mensaje"],
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
            justify="left",
        ).grid(row=2, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.muller_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        encabezados = [
            "n",
            "P0",
            "P1",
            "P2",
            "Aprox P3",
            "Error",
        ]

        for columna, texto in enumerate(encabezados):
            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#1f2937",
                corner_radius=6,
                width=125,
                height=30,
            ).grid(row=0, column=columna, padx=3, pady=4, sticky="ew")

        for fila_indice, fila in enumerate(datos["tabla"], start=1):
            valores = [
                fila["n"],
                self.formatear_numero_muller(fila["p0"]),
                self.formatear_numero_muller(fila["p1"]),
                self.formatear_numero_muller(fila["p2"]),
                self.formatear_numero_muller(fila["p3"]),
                f"{float(fila['error']):.6f}",
            ]

            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    font=("Arial", 12),
                    text_color="#e8edf7",
                    fg_color="#151a22",
                    corner_radius=6,
                    width=125,
                    height=28,
                ).grid(row=fila_indice, column=columna, padx=3, pady=3, sticky="ew")

    def mostrar_error_muller(self, mensaje):
        self.limpiar_tabla_muller()

        ctk.CTkLabel(
            self.muller_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.muller_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")



    # =========================================================
    # PANTALLA ESPECIAL: LAGRANGE
    # =========================================================

    def mostrar_lagrange(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Lagrange",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(3, weight=1)

        self.lag_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Escribe f(x), indica cuántos xᵢ usarás y el programa calcula yᵢ = f(xᵢ).",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.lag_funcion = self.crear_input_lagrange(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: x**2 + 2*x + 1"
        )

        self.construir_calculadora_lagrange(panel_entrada, 4)

        self.lag_num_puntos = self.crear_input_lagrange(
            panel_entrada,
            5,
            "Cantidad de puntos xᵢ",
            "Ejemplo: 4"
        )

        ctk.CTkButton(
            panel_entrada,
            text="Crear tabla de xᵢ",
            command=self.crear_tabla_puntos_lagrange,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(8, 12), sticky="ew")

        self.lag_puntos_frame = ctk.CTkScrollableFrame(
            panel_entrada,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
            height=260,
        )
        self.lag_puntos_frame.grid(row=8, column=0, padx=22, pady=(0, 14), sticky="ew")
        self.lag_puntos_frame.grid_columnconfigure(0, weight=1)
        self.lag_puntos_frame.grid_columnconfigure(1, weight=1)
        self.lag_puntos_frame.grid_columnconfigure(2, weight=1)

        self.crear_label(
            self.lag_puntos_frame,
            "Primero crea la tabla y escribe los xᵢ.",
            tamano=13,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self.lag_x_entries = []
        self.lag_y_labels = []

        ctk.CTkButton(
            panel_entrada,
            text="Evaluar yᵢ y calcular polinomio",
            command=self.calcular_lagrange,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=9, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.lag_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.lag_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.lag_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.lag_grafica_frame,
            "Aquí aparecerá f(x) original, P(x) interpolante y los puntos calculados.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.lag_resultado_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.lag_resultado_frame.grid(row=3, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.lag_resultado_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.lag_resultado_frame,
            "Aquí aparecerá el polinomio final y el procedimiento.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_lagrange(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def construir_calculadora_lagrange(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_lagrange
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_lagrange
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_lagrange(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_lagrange(self, texto):
        self.lag_funcion.insert("end", texto)
        self.lag_funcion.focus()

    def limpiar_funcion_lagrange(self):
        self.lag_funcion.delete(0, "end")
        self.lag_funcion.focus()

    def borrar_funcion_lagrange(self):
        texto = self.lag_funcion.get()
        self.lag_funcion.delete(0, "end")
        self.lag_funcion.insert(0, texto[:-1])
        self.lag_funcion.focus()

    def crear_tabla_puntos_lagrange(self):
        for widget in self.lag_puntos_frame.winfo_children():
            widget.destroy()

        self.lag_x_entries = []
        self.lag_y_labels = []

        try:
            n = int(self.lag_num_puntos.get())

            if n < 2:
                raise ValueError("Necesitas al menos 2 puntos.")

            if n > 20:
                raise ValueError("Para que se vea bien, usa máximo 20 puntos.")

            encabezados = ["i", "xᵢ", "yᵢ = f(xᵢ)"]
            for columna, texto in enumerate(encabezados):
                ctk.CTkLabel(
                    self.lag_puntos_frame,
                    text=texto,
                    font=("Arial", 13, "bold"),
                    text_color="#ffffff",
                    fg_color="#1f2937",
                    corner_radius=6,
                    height=30,
                ).grid(row=0, column=columna, padx=5, pady=(12, 6), sticky="ew")

            for i in range(n):
                ctk.CTkLabel(
                    self.lag_puntos_frame,
                    text=str(i),
                    font=("Arial", 13, "bold"),
                    text_color="#dbeafe",
                    fg_color="#101216",
                    corner_radius=6,
                    height=34,
                ).grid(row=i + 1, column=0, padx=5, pady=4, sticky="ew")

                entrada_x = ctk.CTkEntry(
                    self.lag_puntos_frame,
                    placeholder_text=f"x{i}",
                    height=34,
                    corner_radius=8,
                    fg_color="#0f141b",
                    border_color="#344054",
                    text_color="#ffffff",
                    font=("Arial", 13),
                )
                entrada_x.grid(row=i + 1, column=1, padx=5, pady=4, sticky="ew")

                label_y = ctk.CTkLabel(
                    self.lag_puntos_frame,
                    text="Se calcula solo",
                    font=("Arial", 13, "bold"),
                    text_color="#9fb0c7",
                    fg_color="#101216",
                    corner_radius=6,
                    height=34,
                )
                label_y.grid(row=i + 1, column=2, padx=5, pady=4, sticky="ew")

                self.lag_x_entries.append(entrada_x)
                self.lag_y_labels.append(label_y)

        except Exception as error:
            ctk.CTkLabel(
                self.lag_puntos_frame,
                text=f"Error: {error}",
                font=("Arial", 13, "bold"),
                text_color="#fca5a5",
                wraplength=540,
                justify="left",
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

    def limpiar_grafica_lagrange(self):
        for widget in self.lag_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_resultado_lagrange(self):
        for widget in self.lag_resultado_frame.winfo_children():
            widget.destroy()

    def formatear_decimal_lagrange(self, valor, decimales=6):
        try:
            valor_decimal = float(sp.N(valor, 15))
            return f"{valor_decimal:.{decimales}f}"
        except Exception:
            try:
                valor_decimal = float(valor)
                return f"{valor_decimal:.{decimales}f}"
            except Exception:
                return str(valor)

    def calcular_lagrange(self):
        try:
            if not self.lag_x_entries:
                raise ValueError("Primero crea la tabla de xᵢ.")

            funcion = self.lag_funcion.get()
            valores_x = [entrada_x.get() for entrada_x in self.lag_x_entries]

            datos = self.metodo_actual.calcular_detallado(
                funcion=funcion,
                valores_x=valores_x,
            )

            for etiqueta, punto in zip(self.lag_y_labels, datos["puntos"]):
                etiqueta.configure(
                    text=self.formatear_decimal_lagrange(punto[1], 6),
                    text_color="#9fffe4",
                )

            self.dibujar_grafica_lagrange(datos)
            self.mostrar_resultado_lagrange(datos)

        except Exception as error:
            self.mostrar_error_lagrange(str(error))

    def dibujar_grafica_lagrange(self, datos):
        self.limpiar_grafica_lagrange()

        puntos = datos["puntos_float"]
        polinomio_numpy = datos.get("polinomio_numpy", datos["funcion_numpy"])
        funcion_original_numpy = datos.get("funcion_original_numpy")

        xs_puntos = np.array([p[0] for p in puntos], dtype=float)
        ys_puntos = np.array([p[1] for p in puntos], dtype=float)

        x_min = float(np.min(xs_puntos))
        x_max = float(np.max(xs_puntos))
        ancho = x_max - x_min

        if ancho == 0:
            ancho = 1.0

        margen_x = ancho * 0.45
        x_ini = x_min - margen_x
        x_fin = x_max + margen_x

        xs = np.linspace(x_ini, x_fin, 900)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            ys_polinomio = polinomio_numpy(xs)

        ys_polinomio = np.array(ys_polinomio, dtype=float)
        mascara = np.isfinite(ys_polinomio)
        xs_validos = xs[mascara]
        ys_validos = ys_polinomio[mascara]

        xs_funcion_validos = np.array([])
        ys_funcion_validos = np.array([])
        if funcion_original_numpy is not None:
            with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
                try:
                    ys_funcion = funcion_original_numpy(xs)
                except Exception:
                    ys_funcion = np.array([funcion_original_numpy(float(valor_x)) for valor_x in xs])
            ys_funcion = np.array(ys_funcion, dtype=float)
            mascara_funcion = np.isfinite(ys_funcion)
            xs_funcion_validos = xs[mascara_funcion]
            ys_funcion_validos = ys_funcion[mascara_funcion]

        valores_y = list(ys_validos) + list(ys_puntos) + list(ys_funcion_validos)
        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        if len(valores_y) == 0:
            y_min, y_max = -1, 1
        else:
            y_min = float(np.min(valores_y))
            y_max = float(np.max(valores_y))

        if y_min == y_max:
            y_min -= 1
            y_max += 1

        margen_y = abs(y_max - y_min) * 0.20
        y_min -= margen_y
        y_max += margen_y

        figura = Figure(figsize=(7.4, 3.8), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        # Primero se dibuja el polinomio interpolante.
        # Luego se dibuja encima la función original para que no quede escondida.
        eje.plot(
            xs_validos,
            ys_validos,
            linewidth=2,
            color="#7cc7ff",
            label="P(x) interpolante",
            zorder=2,
        )

        if len(xs_funcion_validos) > 0:
            eje.plot(
                xs_funcion_validos,
                ys_funcion_validos,
                linewidth=3,
                linestyle="--",
                color="#ff4fd8",
                label="f(x) original",
                zorder=4,
            )

        eje.scatter(xs_puntos, ys_puntos, color="#f28c28", s=80, label="(xᵢ, f(xᵢ))", zorder=6)

        for i, (xi, yi) in enumerate(puntos):
            eje.annotate(
                f"P{i}",
                (xi, yi),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#f28c28",
                fontsize=11,
                fontweight="bold",
            )

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.60)
        if x_ini <= 0 <= x_fin:
            eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        eje.set_xlim(x_ini, x_fin)
        eje.set_ylim(y_min, y_max)
        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Comparación: función original vs polinomio de Lagrange", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x) / P(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")
            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.lag_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_resultado_lagrange(self, datos):
        self.limpiar_resultado_lagrange()
        self.lag_resultado_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.lag_resultado_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Polinomio interpolante",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"f(x) = {datos.get('funcion_texto', '')}",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
            wraplength=760,
            justify="left",
        ).grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"P(x) = {datos['polinomio_texto']}",
            font=("Arial", 18, "bold"),
            text_color="#9fffe4",
            wraplength=760,
            justify="left",
        ).grid(row=2, column=0, padx=16, pady=(0, 8), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"Forma factorizada: {datos['polinomio_factorizado_texto']}",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
            wraplength=760,
            justify="left",
        ).grid(row=3, column=0, padx=16, pady=(0, 8), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text="La gráfica compara automáticamente f(x) original contra P(x) interpolante.",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
            wraplength=760,
            justify="left",
        ).grid(row=4, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.lag_resultado_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        encabezados = ["i", "xᵢ", "yᵢ=f(xᵢ)", "Lᵢ(x) resultante"]

        for columna, texto in enumerate(encabezados):
            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#1f2937",
                corner_radius=6,
                width=150,
                height=30,
            ).grid(row=0, column=columna, padx=3, pady=4, sticky="ew")

        for fila_indice, fila in enumerate(datos["tabla"], start=1):
            valores = [
                fila["i"],
                self.formatear_decimal_lagrange(fila["xi"], 6),
                self.formatear_decimal_lagrange(fila["yi"], 6),
                fila.get("Li_producto_texto", sp.sstr(sp.simplify(fila["Li"]))),
            ]

            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    font=("Arial", 12),
                    text_color="#e8edf7",
                    fg_color="#151a22",
                    corner_radius=6,
                    width=150,
                    height=28,
                    wraplength=260,
                ).grid(row=fila_indice, column=columna, padx=3, pady=3, sticky="ew")

        procedimiento = ctk.CTkTextbox(
            self.lag_resultado_frame,
            height=260,
            wrap="word",
            corner_radius=12,
            fg_color="#101216",
            border_width=1,
            border_color="#303846",
            text_color="#e8edf7",
            font=("Consolas", 13),
        )
        procedimiento.grid(row=2, column=0, padx=14, pady=(0, 18), sticky="ew")

        texto = ""
        texto += "Fórmula general:\n"
        texto += "P(x) = Σ y_i L_i(x)\n"
        texto += "y_i = f(x_i)\n"
        texto += "L_i(x) = Π (x - x_j)/(x_i - x_j), con j ≠ i\n\n"

        texto += "Evaluaciones:\n"

        for fila in datos["tabla"]:
            xi_decimal = self.formatear_decimal_lagrange(fila["xi"], 6)
            yi_decimal = self.formatear_decimal_lagrange(fila["yi"], 6)
            texto += f"y_{fila['i']} = f({xi_decimal}) = {yi_decimal}\n"

        texto += "\nBases Lᵢ(x) resultantes:\n"

        for fila in datos["tabla"]:
            texto += f"L_{fila['i']}(x) = {fila.get('Li_producto_texto', sp.sstr(sp.simplify(fila['Li'])))}\n"
            if "Li_expandido_texto" in fila:
                texto += f"L_{fila['i']}(x) expandido = {fila['Li_expandido_texto']}\n"
            texto += "\n"

        texto += f"Polinomio expandido:\nP(x) = {datos['polinomio_texto']}\n"

        procedimiento.insert("1.0", texto)
        procedimiento.configure(state="disabled")

    def mostrar_error_lagrange(self, mensaje):
        self.limpiar_resultado_lagrange()

        ctk.CTkLabel(
            self.lag_resultado_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.lag_resultado_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")


    # =========================================================
    # PANTALLA ESPECIAL: DIFERENCIAS DIVIDIDAS
    # =========================================================

    def mostrar_diferencias_divididas(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Diferencias divididas",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=2)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.dd_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Escribe f(x), define los puntos xᵢ y calcula la tabla de diferencias divididas.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.dd_funcion = self.crear_input_dd(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: 3*x**2*sin(x)"
        )

        self.construir_calculadora_dd(panel_entrada, 4)

        self.dd_modo_fijo = "Adelante"

        self.dd_cantidad = self.crear_input_dd(
            panel_entrada,
            5,
            "Cantidad de puntos xᵢ",
            "Ejemplo: 6"
        )

        ctk.CTkButton(
            panel_entrada,
            text="Crear tabla de xᵢ",
            command=self.crear_tabla_x_dd,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(10, 12), sticky="ew")

        self.dd_puntos_frame = ctk.CTkScrollableFrame(
            panel_entrada,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
            height=180,
        )
        self.dd_puntos_frame.grid(row=8, column=0, padx=22, pady=(0, 14), sticky="ew")
        self.dd_puntos_frame.grid_columnconfigure(0, weight=0)
        self.dd_puntos_frame.grid_columnconfigure(1, weight=1)
        self.dd_puntos_frame.grid_columnconfigure(2, weight=1)

        self.crear_label(
            self.dd_puntos_frame,
            "Crea la tabla y escribe los valores xᵢ. Los yᵢ=f(xᵢ) se calculan solos.",
            tamano=13,
            color="#cbd5e1",
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=12, sticky="w")

        self.dd_x_entries = []
        self.dd_y_labels = []

        ctk.CTkButton(
            panel_entrada,
            text="Evaluar yᵢ y calcular polinomio",
            command=self.calcular_diferencias_divididas,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=11, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.dd_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.dd_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.dd_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.dd_grafica_frame,
            "Aquí aparecerá f(x), P(x) y los puntos usados.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.dd_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.dd_tabla_frame.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.dd_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.dd_tabla_frame,
            "Aquí aparecerá la tabla de diferencias divididas y el polinomio.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_dd(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def construir_calculadora_dd(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_dd
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_dd
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_dd(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_dd(self, texto):
        self.dd_funcion.insert("end", texto)
        self.dd_funcion.focus()

    def limpiar_funcion_dd(self):
        self.dd_funcion.delete(0, "end")
        self.dd_funcion.focus()

    def borrar_funcion_dd(self):
        texto = self.dd_funcion.get()
        self.dd_funcion.delete(0, "end")
        self.dd_funcion.insert(0, texto[:-1])
        self.dd_funcion.focus()

    def crear_tabla_x_dd(self):
        for widget in self.dd_puntos_frame.winfo_children():
            widget.destroy()

        self.dd_x_entries = []
        self.dd_y_labels = []

        try:
            cantidad = int(self.dd_cantidad.get())

            if cantidad < 2:
                raise ValueError("Necesitas al menos 2 puntos.")

            if cantidad > 12:
                raise ValueError("Para que la tabla se vea bien, usa máximo 12 puntos.")

            encabezados = ["i", "xᵢ", "yᵢ = f(xᵢ)"]
            for columna, texto in enumerate(encabezados):
                ctk.CTkLabel(
                    self.dd_puntos_frame,
                    text=texto,
                    font=("Arial", 12, "bold"),
                    text_color="#ffffff",
                    fg_color="#1f2937",
                    corner_radius=6,
                    height=28,
                ).grid(row=0, column=columna, padx=4, pady=6, sticky="ew")

            for i in range(cantidad):
                ctk.CTkLabel(
                    self.dd_puntos_frame,
                    text=str(i),
                    font=("Arial", 12, "bold"),
                    text_color="#ffffff",
                    fg_color="#101216",
                    corner_radius=6,
                    width=44,
                    height=32,
                ).grid(row=i + 1, column=0, padx=4, pady=4, sticky="ew")

                entrada = ctk.CTkEntry(
                    self.dd_puntos_frame,
                    height=32,
                    corner_radius=8,
                    fg_color="#0f141b",
                    border_color="#344054",
                    text_color="#ffffff",
                    font=("Arial", 13),
                )
                entrada.grid(row=i + 1, column=1, padx=4, pady=4, sticky="ew")
                self.dd_x_entries.append(entrada)

                etiqueta_y = ctk.CTkLabel(
                    self.dd_puntos_frame,
                    text="—",
                    font=("Arial", 12, "bold"),
                    text_color="#9fffe4",
                    fg_color="#101216",
                    corner_radius=6,
                    height=32,
                )
                etiqueta_y.grid(row=i + 1, column=2, padx=4, pady=4, sticky="ew")
                self.dd_y_labels.append(etiqueta_y)

        except Exception as error:
            ctk.CTkLabel(
                self.dd_puntos_frame,
                text=f"Error: {error}",
                font=("Arial", 13, "bold"),
                text_color="#fca5a5",
                wraplength=520,
                justify="left",
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

    def limpiar_grafica_dd(self):
        for widget in self.dd_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_dd(self):
        for widget in self.dd_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_dd(self, valor, decimales=6):
        if valor is None:
            return ""
        try:
            return f"{float(valor):.{decimales}f}"
        except Exception:
            return str(valor)

    def calcular_diferencias_divididas(self):
        try:
            if not self.dd_x_entries:
                raise ValueError("Primero crea la tabla de xᵢ.")

            puntos_x = [entrada.get() for entrada in self.dd_x_entries]

            datos = self.metodo_actual.calcular_detallado(
                funcion=self.dd_funcion.get(),
                puntos_x=puntos_x,
                modo=self.dd_modo_fijo,
            )

            for etiqueta, yi in zip(self.dd_y_labels, datos["puntos_y_originales"]):
                etiqueta.configure(text=self.formatear_numero_dd(yi, 6))

            self.dibujar_grafica_dd(datos)
            self.mostrar_resultado_dd(datos)

        except Exception as error:
            self.mostrar_error_dd(str(error))

    def dibujar_grafica_dd(self, datos):
        self.limpiar_grafica_dd()

        puntos_x = datos["puntos_x_originales"]
        puntos_y = datos["puntos_y_originales"]
        funcion_numpy = datos["funcion_numpy"]
        polinomio_numpy = datos["polinomio_numpy"]

        x_min = min(puntos_x)
        x_max = max(puntos_x)
        ancho = x_max - x_min

        if ancho == 0:
            ancho = 1

        margen = ancho * 0.45
        x_inicio = x_min - margen
        x_final = x_max + margen

        xs = np.linspace(x_inicio, x_final, 900)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys_funcion = funcion_numpy(xs)
            except Exception:
                ys_funcion = np.array([funcion_numpy(float(valor)) for valor in xs])

            try:
                ys_polinomio = polinomio_numpy(xs)
            except Exception:
                ys_polinomio = np.array([polinomio_numpy(float(valor)) for valor in xs])

        ys_funcion = np.array(ys_funcion, dtype=float)
        ys_polinomio = np.array(ys_polinomio, dtype=float)

        mascara_funcion = np.isfinite(ys_funcion)
        mascara_polinomio = np.isfinite(ys_polinomio)

        figura = Figure(figsize=(7.6, 3.9), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(
            xs[mascara_polinomio],
            ys_polinomio[mascara_polinomio],
            linewidth=2,
            color="#7cc7ff",
            label="P(x) interpolante",
            zorder=2,
        )

        eje.plot(
            xs[mascara_funcion],
            ys_funcion[mascara_funcion],
            linewidth=3,
            linestyle="--",
            color="#ff4fd8",
            label="f(x) original",
            zorder=4,
        )

        eje.scatter(
            puntos_x,
            puntos_y,
            s=70,
            color="#f28c28",
            label="(xᵢ, f(xᵢ))",
            zorder=6,
        )

        for i, (xi, yi) in enumerate(zip(puntos_x, puntos_y)):
            eje.annotate(
                f"P{i}",
                (xi, yi),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#f28c28",
                fontsize=11,
                fontweight="bold",
            )

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.65)

        if x_inicio <= 0 <= x_final:
            eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        valores_y = []
        valores_y.extend(ys_funcion[mascara_funcion])
        valores_y.extend(ys_polinomio[mascara_polinomio])
        valores_y.extend(puntos_y)
        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        if len(valores_y) > 0:
            y_min = np.min(valores_y)
            y_max = np.max(valores_y)

            if y_min == y_max:
                y_min -= 1
                y_max += 1

            margen_y = abs(y_max - y_min) * 0.18
            eje.set_ylim(y_min - margen_y, y_max + margen_y)

        eje.set_xlim(x_inicio, x_final)
        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Diferencias divididas", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x) / P(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")
            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.dd_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_resultado_dd(self, datos):
        self.limpiar_tabla_dd()
        self.dd_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.dd_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Polinomio por diferencias divididas",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=datos["polinomio_newton"],
            font=("Consolas", 13, "bold"),
            text_color="#ffffff",
            wraplength=980,
            justify="left",
        ).grid(row=1, column=0, padx=16, pady=(0, 10), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text="Forma expandida:",
            font=("Arial", 13, "bold"),
            text_color="#9fffe4",
        ).grid(row=2, column=0, padx=16, pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"P(x) = {datos['polinomio_expandido']}",
            font=("Consolas", 13, "bold"),
            text_color="#9fffe4",
            wraplength=980,
            justify="left",
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        # =====================================================
        # TABLA TIPO EXCEL / APUNTES
        # En lugar de poner todas las diferencias en filas rectas,
        # se colocan escalonadas como en tus apuntes:
        # x0, x1, x2... y las diferencias entre filas.
        # =====================================================
        tabla = ctk.CTkFrame(
            self.dd_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        n = len(datos["puntos_x"])
        total_columnas = n + 2       # n, xi, f(xi), dif orden 1, ..., dif orden n-1
        total_filas = 2 * n          # encabezado + filas escalonadas

        for columna in range(total_columnas):
            tabla.grid_columnconfigure(columna, weight=1)

        def celda(padre, fila, columna, texto="", ancho=118, alto=30,
                  color_fondo="#151a22", color_texto="#e8edf7",
                  fuente=("Arial", 12, "bold")):
            etiqueta = ctk.CTkLabel(
                padre,
                text=texto,
                font=fuente,
                text_color=color_texto,
                fg_color=color_fondo,
                corner_radius=6,
                width=ancho,
                height=alto,
            )
            etiqueta.grid(row=fila, column=columna, padx=3, pady=3, sticky="ew")
            return etiqueta

        encabezados = ["n", "xᵢ", "f(xᵢ)"]
        for orden in range(1, n):
            encabezados.append(f"Dif. {orden}")

        for columna, texto in enumerate(encabezados):
            celda(
                tabla,
                0,
                columna,
                texto,
                ancho=118,
                alto=32,
                color_fondo="#1f2937",
                color_texto="#ffffff",
                fuente=("Arial", 12, "bold"),
            )

        # Crear fondo vacío para que la tabla conserve forma de hoja de cálculo.
        for fila in range(1, total_filas):
            for columna in range(total_columnas):
                celda(
                    tabla,
                    fila,
                    columna,
                    "",
                    ancho=118,
                    alto=28,
                    color_fondo="#0f141b",
                    color_texto="#e8edf7",
                    fuente=("Arial", 12, "bold"),
                )

        # Colocar xᵢ y f(xᵢ) en filas alternadas: x0, x1, x2...
        for i, (xi, yi) in enumerate(zip(datos["puntos_x"], datos["puntos_y"])):
            fila_visual = 1 + (2 * i)

            celda(
                tabla,
                fila_visual,
                0,
                f"x{i}",
                color_fondo="#111827",
                color_texto="#ffffff",
                fuente=("Arial", 12, "bold"),
            )
            celda(
                tabla,
                fila_visual,
                1,
                self.formatear_numero_dd(xi, 6),
                color_fondo="#111827",
                color_texto="#ffffff",
                fuente=("Arial", 12, "bold"),
            )
            es_fx0 = (i == 0)
            celda(
                tabla,
                fila_visual,
                2,
                self.formatear_numero_dd(yi, 8),
                color_fondo="#172238" if es_fx0 else "#111827",
                color_texto="#9fffe4" if es_fx0 else "#ffffff",
                fuente=ctk.CTkFont(family="Arial", size=12, weight="bold", underline=True) if es_fx0 else ("Arial", 12, "bold"),
            )

        # Colocar diferencias divididas en diagonal/escalón.
        # tabla[i][orden] corresponde a f[xᵢ, ..., xᵢ₊orden].
        tabla_diferencias = datos["tabla"]
        for orden in range(1, n):
            for i in range(n - orden):
                valor = tabla_diferencias[i][orden]
                fila_visual = 1 + (2 * i) + orden
                columna_visual = 2 + orden

                # En Newton hacia adelante/atrás los coeficientes usados son la fila superior
                # de la tabla ordenada, por eso se resaltan en verde agua.
                es_coeficiente = (i == 0)
                color_texto = "#9fffe4" if es_coeficiente else "#ffffff"
                color_fondo = "#172238" if es_coeficiente else "#111827"

                celda(
                    tabla,
                    fila_visual,
                    columna_visual,
                    self.formatear_numero_dd(valor, 8),
                    color_fondo=color_fondo,
                    color_texto=color_texto,
                    fuente=("Arial", 12, "bold"),
                )

        # Coeficientes usados en el polinomio
        coef_frame = ctk.CTkFrame(
            self.dd_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        coef_frame.grid(row=2, column=0, padx=14, pady=(0, 14), sticky="ew")
        coef_frame.grid_columnconfigure(0, weight=1)

        texto_coef = "Coeficientes resaltados: "
        texto_coef += ", ".join(
            [f"a{i} = {self.formatear_numero_dd(coef, 8)}" for i, coef in enumerate(datos["coeficientes"])]
        )

        ctk.CTkLabel(
            coef_frame,
            text=texto_coef,
            font=("Consolas", 13, "bold"),
            text_color="#ffffff",
            wraplength=980,
            justify="left",
        ).grid(row=0, column=0, padx=14, pady=14, sticky="w")

    def mostrar_error_dd(self, mensaje):
        self.limpiar_tabla_dd()

        ctk.CTkLabel(
            self.dd_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.dd_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=720,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")


    # =========================================================
    # PANTALLA ESPECIAL: NEVILLE SIN VALOR X A INTERPOLAR
    # =========================================================

    def mostrar_neville(self):
        self.limpiar_pantalla()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#102d52",
            corner_radius=0,
            border_width=0,
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            encabezado,
            text="← Inicio",
            command=self.mostrar_inicio,
            width=110,
            height=34,
            fg_color="#1a1f2b",
            hover_color="#243044",
            border_width=1,
            border_color="#496386",
        ).grid(row=0, column=0, padx=22, pady=18, sticky="w")

        self.crear_label(
            encabezado,
            "Neville",
            tamano=26,
            peso="bold",
            color="#ffffff",
        ).grid(row=0, column=1, padx=10, pady=18, sticky="w")

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.grid(row=1, column=0, padx=28, pady=24, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=2)
        cuerpo.grid_rowconfigure(0, weight=1)

        panel_entrada = ctk.CTkScrollableFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_entrada.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        panel_entrada.grid_columnconfigure(0, weight=1)

        panel_resultado = ctk.CTkFrame(
            cuerpo,
            fg_color="#101216",
            corner_radius=16,
            border_width=1,
            border_color="#303846",
        )
        panel_resultado.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        panel_resultado.grid_columnconfigure(0, weight=1)
        panel_resultado.grid_rowconfigure(2, weight=1)

        self.nev_resultado_panel = panel_resultado

        self.crear_label(
            panel_entrada,
            "DATOS DE ENTRADA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.crear_label(
            panel_entrada,
            "Escribe f(x), define los puntos xᵢ y calcula el polinomio por Neville.",
            tamano=18,
            peso="bold",
            color="#ffffff",
        ).grid(row=1, column=0, padx=22, pady=(4, 16), sticky="w")

        self.nev_funcion = self.crear_input_neville(
            panel_entrada,
            2,
            "Función f(x)",
            "Ejemplo: 3*x**2*sin(x)"
        )

        self.construir_calculadora_neville(panel_entrada, 4)

        self.nev_cantidad = self.crear_input_neville(
            panel_entrada,
            5,
            "Cantidad de puntos xᵢ",
            "Ejemplo: 6"
        )

        ctk.CTkButton(
            panel_entrada,
            text="Crear tabla de xᵢ",
            command=self.crear_tabla_x_neville,
            height=40,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#1f6feb",
            hover_color="#1959bd",
        ).grid(row=7, column=0, padx=22, pady=(10, 12), sticky="ew")

        self.nev_puntos_frame = ctk.CTkScrollableFrame(
            panel_entrada,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
            height=180,
        )
        self.nev_puntos_frame.grid(row=8, column=0, padx=22, pady=(0, 14), sticky="ew")
        self.nev_puntos_frame.grid_columnconfigure(0, weight=0)
        self.nev_puntos_frame.grid_columnconfigure(1, weight=1)
        self.nev_puntos_frame.grid_columnconfigure(2, weight=1)

        self.crear_label(
            self.nev_puntos_frame,
            "Crea la tabla y escribe los valores xᵢ. Los yᵢ=f(xᵢ) se calculan solos.",
            tamano=13,
            color="#cbd5e1",
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=12, sticky="w")

        self.nev_x_entries = []
        self.nev_y_labels = []

        ctk.CTkButton(
            panel_entrada,
            text="Evaluar yᵢ y calcular polinomio",
            command=self.calcular_neville,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color="#159a73",
            hover_color="#0f7a5d",
        ).grid(row=11, column=0, padx=22, pady=(0, 24), sticky="ew")

        self.crear_label(
            panel_resultado,
            "GRÁFICA",
            tamano=11,
            peso="bold",
            color="#75b8ff",
        ).grid(row=0, column=0, padx=22, pady=(22, 0), sticky="w")

        self.nev_grafica_frame = ctk.CTkFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.nev_grafica_frame.grid(row=1, column=0, padx=22, pady=(10, 14), sticky="ew")
        self.nev_grafica_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.nev_grafica_frame,
            "Aquí aparecerá f(x), P(x) de Neville y los puntos usados.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

        self.nev_tabla_frame = ctk.CTkScrollableFrame(
            panel_resultado,
            fg_color="#151a22",
            corner_radius=12,
            border_width=1,
            border_color="#2a3342",
        )
        self.nev_tabla_frame.grid(row=2, column=0, padx=22, pady=(0, 22), sticky="nsew")
        self.nev_tabla_frame.grid_columnconfigure(0, weight=1)

        self.crear_label(
            self.nev_tabla_frame,
            "Aquí aparecerá la tabla triangular de Neville y el polinomio.",
            tamano=14,
            color="#cbd5e1",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def crear_input_neville(self, padre, fila, texto, placeholder=""):
        ctk.CTkLabel(
            padre,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#f1f5ff",
        ).grid(row=fila, column=0, padx=22, pady=(10, 4), sticky="w")

        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=38,
            corner_radius=9,
            fg_color="#0f141b",
            border_color="#344054",
            text_color="#ffffff",
            font=("Arial", 14),
        )
        entrada.grid(row=fila + 1, column=0, padx=22, pady=(0, 8), sticky="ew")
        return entrada

    def construir_calculadora_neville(self, padre, fila):
        calculadora = ctk.CTkFrame(
            padre,
            fg_color="#151a22",
            corner_radius=14,
            border_width=1,
            border_color="#2a3342",
        )
        calculadora.grid(row=fila, column=0, padx=22, pady=(8, 10), sticky="ew")

        for columna in range(4):
            calculadora.grid_columnconfigure(columna, weight=1)

        botones = [
            ("x", "x"), ("sin", "sin("), ("cos", "cos("), ("C", "clear"),
            ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
            ("x²", "**2"), ("xʸ", "**"), ("eˣ", "exp("), ("ln", "log("),
            ("(", "("), (")", ")"), ("π", "pi"), ("⌫", "back"),
        ]

        for i, (texto, valor) in enumerate(botones):
            fila_boton = i // 4
            columna_boton = i % 4

            if valor == "clear":
                comando = self.limpiar_funcion_neville
                color = "#dc2626"
                hover = "#b91c1c"
            elif valor == "back":
                comando = self.borrar_funcion_neville
                color = "#0ea5e9"
                hover = "#0284c7"
            else:
                comando = lambda v=valor: self.insertar_funcion_neville(v)
                color = "#1a1f2b"
                hover = "#243044"

            ctk.CTkButton(
                calculadora,
                text=texto,
                command=comando,
                height=42,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#343c4c",
                text_color="#ffffff",
                font=("Arial", 14, "bold"),
            ).grid(row=fila_boton, column=columna_boton, padx=6, pady=6, sticky="ew")

    def insertar_funcion_neville(self, texto):
        self.nev_funcion.insert("end", texto)
        self.nev_funcion.focus()

    def limpiar_funcion_neville(self):
        self.nev_funcion.delete(0, "end")
        self.nev_funcion.focus()

    def borrar_funcion_neville(self):
        texto = self.nev_funcion.get()
        self.nev_funcion.delete(0, "end")
        self.nev_funcion.insert(0, texto[:-1])
        self.nev_funcion.focus()

    def crear_tabla_x_neville(self):
        for widget in self.nev_puntos_frame.winfo_children():
            widget.destroy()

        self.nev_x_entries = []
        self.nev_y_labels = []

        try:
            cantidad = int(self.nev_cantidad.get())

            if cantidad < 2:
                raise ValueError("Neville necesita al menos 2 puntos.")

            if cantidad > 12:
                raise ValueError("Para que la tabla se vea bien, usa máximo 12 puntos.")

            encabezados = ["i", "xᵢ", "yᵢ = f(xᵢ)"]

            for columna, texto in enumerate(encabezados):
                ctk.CTkLabel(
                    self.nev_puntos_frame,
                    text=texto,
                    font=("Arial", 12, "bold"),
                    text_color="#ffffff",
                    fg_color="#1f2937",
                    corner_radius=6,
                    height=28,
                ).grid(row=0, column=columna, padx=4, pady=4, sticky="ew")

            for i in range(cantidad):
                ctk.CTkLabel(
                    self.nev_puntos_frame,
                    text=str(i),
                    font=("Arial", 12, "bold"),
                    text_color="#ffffff",
                    fg_color="#101216",
                    corner_radius=6,
                    width=44,
                    height=32,
                ).grid(row=i + 1, column=0, padx=4, pady=4, sticky="ew")

                entrada = ctk.CTkEntry(
                    self.nev_puntos_frame,
                    placeholder_text=f"x{i}",
                    height=32,
                    corner_radius=8,
                    fg_color="#0f141b",
                    border_color="#344054",
                    text_color="#ffffff",
                    font=("Arial", 13),
                )
                entrada.grid(row=i + 1, column=1, padx=4, pady=4, sticky="ew")
                self.nev_x_entries.append(entrada)

                etiqueta_y = ctk.CTkLabel(
                    self.nev_puntos_frame,
                    text="—",
                    font=("Arial", 12, "bold"),
                    text_color="#9fffe4",
                    fg_color="#101216",
                    corner_radius=6,
                    height=32,
                )
                etiqueta_y.grid(row=i + 1, column=2, padx=4, pady=4, sticky="ew")
                self.nev_y_labels.append(etiqueta_y)

        except Exception as error:
            ctk.CTkLabel(
                self.nev_puntos_frame,
                text=f"Error: {error}",
                font=("Arial", 13, "bold"),
                text_color="#fca5a5",
                wraplength=520,
                justify="left",
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

    def limpiar_grafica_neville(self):
        for widget in self.nev_grafica_frame.winfo_children():
            widget.destroy()

    def limpiar_tabla_neville(self):
        for widget in self.nev_tabla_frame.winfo_children():
            widget.destroy()

    def formatear_numero_neville(self, valor, decimales=6):
        if valor is None:
            return ""
        try:
            return f"{float(valor):.{decimales}f}"
        except Exception:
            return str(valor)

    def calcular_neville(self):
        try:
            if not self.nev_x_entries:
                raise ValueError("Primero crea la tabla de xᵢ.")

            puntos_x = [entrada.get() for entrada in self.nev_x_entries]

            datos = self.metodo_actual.calcular_detallado(
                funcion=self.nev_funcion.get(),
                puntos_x=puntos_x,
            )

            for etiqueta, yi in zip(self.nev_y_labels, datos["puntos_y"]):
                etiqueta.configure(text=self.formatear_numero_neville(yi, 6))

            self.dibujar_grafica_neville(datos)
            self.mostrar_resultado_neville(datos)

        except Exception as error:
            self.mostrar_error_neville(str(error))

    def dibujar_grafica_neville(self, datos):
        self.limpiar_grafica_neville()

        puntos_x = datos["puntos_x"]
        puntos_y = datos["puntos_y"]
        funcion_numpy = datos["funcion_numpy"]
        polinomio_numpy = datos["polinomio_numpy"]

        x_min = min(puntos_x)
        x_max = max(puntos_x)
        ancho = x_max - x_min

        if ancho == 0:
            ancho = 1

        margen = ancho * 0.45
        x_inicio = x_min - margen
        x_final = x_max + margen

        xs = np.linspace(x_inicio, x_final, 900)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            try:
                ys_funcion = funcion_numpy(xs)
            except Exception:
                ys_funcion = np.array([funcion_numpy(float(valor)) for valor in xs])

            try:
                ys_polinomio = polinomio_numpy(xs)
            except Exception:
                ys_polinomio = np.array([polinomio_numpy(float(valor)) for valor in xs])

        ys_funcion = np.array(ys_funcion, dtype=float)
        ys_polinomio = np.array(ys_polinomio, dtype=float)

        mascara_funcion = np.isfinite(ys_funcion)
        mascara_polinomio = np.isfinite(ys_polinomio)

        figura = Figure(figsize=(7.6, 3.9), dpi=100)
        figura.patch.set_facecolor("#151a22")

        eje = figura.add_subplot(111)
        eje.set_facecolor("#101216")

        eje.plot(
            xs[mascara_polinomio],
            ys_polinomio[mascara_polinomio],
            linewidth=2,
            color="#7cc7ff",
            label="P(x) interpolante",
            zorder=2,
        )

        eje.plot(
            xs[mascara_funcion],
            ys_funcion[mascara_funcion],
            linewidth=3,
            linestyle="--",
            color="#ff4fd8",
            label="f(x) original",
            zorder=4,
        )

        eje.scatter(
            puntos_x,
            puntos_y,
            s=70,
            color="#f28c28",
            label="(xᵢ, f(xᵢ))",
            zorder=6,
        )

        for i, (xi, yi) in enumerate(zip(puntos_x, puntos_y)):
            eje.annotate(
                f"P{i}",
                (xi, yi),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                color="#f28c28",
                fontsize=11,
                fontweight="bold",
            )

        eje.axhline(0, color="#ffffff", linewidth=1, alpha=0.65)

        if x_inicio <= 0 <= x_final:
            eje.axvline(0, color="#ffffff", linewidth=1, alpha=0.25)

        valores_y = []
        valores_y.extend(ys_funcion[mascara_funcion])
        valores_y.extend(ys_polinomio[mascara_polinomio])
        valores_y.extend(puntos_y)
        valores_y = np.array(valores_y, dtype=float)
        valores_y = valores_y[np.isfinite(valores_y)]

        if len(valores_y) > 0:
            y_min = np.min(valores_y)
            y_max = np.max(valores_y)

            if y_min == y_max:
                y_min -= 1
                y_max += 1

            margen_y = abs(y_max - y_min) * 0.18
            eje.set_ylim(y_min - margen_y, y_max + margen_y)

        eje.set_xlim(x_inicio, x_final)
        eje.grid(True, alpha=0.25)
        eje.tick_params(colors="#dbeafe")
        eje.ticklabel_format(useOffset=False)

        eje.spines["bottom"].set_color("#64748b")
        eje.spines["top"].set_color("#64748b")
        eje.spines["left"].set_color("#64748b")
        eje.spines["right"].set_color("#64748b")

        eje.set_title("Interpolación de Neville", color="#ffffff", fontsize=13, fontweight="bold")
        eje.set_xlabel("x", color="#dbeafe")
        eje.set_ylabel("f(x) / P(x)", color="#dbeafe")

        leyenda = eje.legend()
        if leyenda:
            leyenda.get_frame().set_facecolor("#151a22")
            leyenda.get_frame().set_edgecolor("#344054")
            for texto in leyenda.get_texts():
                texto.set_color("#ffffff")

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=self.nev_grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    def mostrar_resultado_neville(self, datos):
        self.limpiar_tabla_neville()
        self.nev_tabla_frame.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            self.nev_tabla_frame,
            fg_color="#172238",
            corner_radius=10,
            border_width=1,
            border_color="#24344f",
        )
        tarjeta.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta,
            text="Polinomio interpolante por Neville",
            font=("Arial", 13, "bold"),
            text_color="#7cc7ff",
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            tarjeta,
            text=f"P(x) = P0,{len(datos['puntos_x']) - 1}(x) = {datos['polinomio_texto']}",
            font=("Consolas", 13, "bold"),
            text_color="#9fffe4",
            wraplength=980,
            justify="left",
        ).grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        tabla = ctk.CTkFrame(
            self.nev_tabla_frame,
            fg_color="#101216",
            corner_radius=12,
            border_width=1,
            border_color="#303846",
        )
        tabla.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")

        n = len(datos["puntos_x"])
        total_columnas = n + 2

        for columna in range(total_columnas):
            tabla.grid_columnconfigure(columna, weight=1)

        def nombre_p(i, j):
            if j == 0:
                return f"P{i}"
            indices = ",".join(str(valor) for valor in range(i, i + j + 1))
            return f"P{indices}"

        def celda(padre, fila, columna, texto="", ancho=150, alto=34,
                  color_fondo="#0f141b", color_texto="#e8edf7",
                  fuente=("Arial", 11, "bold"), wrap=230):
            etiqueta = ctk.CTkLabel(
                padre,
                text=texto,
                font=fuente,
                text_color=color_texto,
                fg_color=color_fondo,
                corner_radius=6,
                width=ancho,
                height=alto,
                wraplength=wrap,
                justify="center",
            )
            etiqueta.grid(row=fila, column=columna, padx=3, pady=3, sticky="ew")
            return etiqueta

        encabezados = ["n", "xᵢ", "Pᵢ = f(xᵢ)"]
        for orden in range(1, n):
            encabezados.append(f"Pᵢ,...,ᵢ+{orden}")

        for columna, texto in enumerate(encabezados):
            celda(
                tabla,
                0,
                columna,
                texto,
                ancho=150,
                alto=34,
                color_fondo="#1f2937",
                color_texto="#ffffff",
                fuente=("Arial", 12, "bold"),
            )

        filas_visuales = 2 * n - 1
        matriz = [["" for _ in range(total_columnas)] for _ in range(filas_visuales)]
        estilos = [["vacio" for _ in range(total_columnas)] for _ in range(filas_visuales)]

        for i, fila in enumerate(datos["tabla"]):
            fila_base = 2 * i
            matriz[fila_base][0] = f"x{i}"
            matriz[fila_base][1] = self.formatear_numero_neville(fila["xi"], 6)
            matriz[fila_base][2] = f"{nombre_p(i, 0)} = f(x{i})\n{self.formatear_numero_neville(fila['yi'], 6)}"
            estilos[fila_base][0] = "dato"
            estilos[fila_base][1] = "dato"
            estilos[fila_base][2] = "base"

            for j in range(1, n - i):
                valor = fila["valores_q_texto"][j]
                fila_nev = fila_base + j
                columna_nev = j + 2
                matriz[fila_nev][columna_nev] = f"{nombre_p(i, j)}(x)\n{valor}"

                if i == 0 and j == n - 1:
                    estilos[fila_nev][columna_nev] = "final"
                else:
                    estilos[fila_nev][columna_nev] = "calculado"

        for fila_indice in range(filas_visuales):
            for columna in range(total_columnas):
                estilo = estilos[fila_indice][columna]
                texto = matriz[fila_indice][columna]

                if estilo == "vacio":
                    color_fondo = "#0f141b"
                    color_texto = "#0f141b"
                    fuente = ("Arial", 11, "bold")
                    alto = 30
                    wrap = 160
                elif estilo == "dato":
                    color_fondo = "#101827"
                    color_texto = "#ffffff"
                    fuente = ("Arial", 12, "bold")
                    alto = 34
                    wrap = 160
                elif estilo == "base":
                    color_fondo = "#172238"
                    color_texto = "#9fffe4"
                    fuente = ("Arial", 12, "bold")
                    alto = 46
                    wrap = 190
                elif estilo == "final":
                    color_fondo = "#1d3a63"
                    color_texto = "#9fffe4"
                    fuente = ("Arial", 12, "bold")
                    alto = 58
                    wrap = 260
                else:
                    color_fondo = "#172238"
                    color_texto = "#e8edf7"
                    fuente = ("Arial", 11, "bold")
                    alto = 54
                    wrap = 260

                celda(
                    tabla,
                    fila_indice + 1,
                    columna,
                    texto,
                    ancho=150,
                    alto=alto,
                    color_fondo=color_fondo,
                    color_texto=color_texto,
                    fuente=fuente,
                    wrap=wrap,
                )

        procedimiento = ctk.CTkTextbox(
            self.nev_tabla_frame,
            height=280,
            wrap="word",
            corner_radius=12,
            fg_color="#101216",
            border_width=1,
            border_color="#303846",
            text_color="#e8edf7",
            font=("Consolas", 13),
        )
        procedimiento.grid(row=2, column=0, padx=14, pady=(0, 18), sticky="ew")

        texto = ""
        texto += "Fórmula general de Neville usando P:\n"
        texto += "Pᵢ(x) = f(xᵢ)\n"
        texto += "Pᵢ,...,ᵢ+j(x) = ((x - xᵢ+j)Pᵢ,...,ᵢ+j-1(x) - (x - xᵢ)Pᵢ+1,...,ᵢ+j(x)) / (xᵢ - xᵢ+j)\n\n"

        texto += "Evaluaciones iniciales:\n"
        for i, (xi, yi) in enumerate(zip(datos["puntos_x"], datos["puntos_y"])):
            texto += f"P{i} = f({self.formatear_numero_neville(xi, 6)}) = {self.formatear_numero_neville(yi, 6)}\n"

        texto += "\nPolinomio final:\n"
        texto += f"P(x) = P0,{len(datos['puntos_x']) - 1}(x) = {datos['polinomio_texto']}\n"

        procedimiento.insert("1.0", texto)
        procedimiento.configure(state="disabled")

    def mostrar_error_neville(self, mensaje):
        self.limpiar_tabla_neville()

        ctk.CTkLabel(
            self.nev_tabla_frame,
            text="No se pudo calcular",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        ctk.CTkLabel(
            self.nev_tabla_frame,
            text=mensaje,
            font=("Arial", 14),
            text_color="#fca5a5",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")


    # =========================================================
    # CALCULO
    # =========================================================

    def calcular(self):
        self.salida_texto.delete("1.0", "end")

        if self.metodo_actual is None:
            self.salida_texto.insert("1.0", "Selecciona un método.")
            return

        try:
            datos = {
                nombre: entrada.get()
                for nombre, entrada in self.entradas.items()
            }

            resultado = self.metodo_actual.ejecutar(**datos)

            texto = ""
            texto += "========================================\n"
            texto += f" MÉTODO: {self.metodo_actual.nombre}\n"
            texto += "========================================\n\n"

            texto += f"Mensaje: {resultado.mensaje}\n\n"

            if resultado.resultado is not None:
                texto += f"Resultado: {resultado.resultado}\n\n"

            if resultado.pasos:
                texto += "PROCEDIMIENTO:\n"
                texto += "----------------------------------------\n"
                for i, paso in enumerate(resultado.pasos, start=1):
                    texto += f"{i}. {paso}\n"
                texto += "\n"

            if resultado.tabla:
                texto += "TABLA:\n"
                texto += "----------------------------------------\n"

                for fila in resultado.tabla:
                    texto += f"{fila}\n"

                texto += "\n"

            if not resultado.pasos and not resultado.tabla and resultado.resultado is None:
                texto += "Este método todavía no devuelve cálculos.\n"

            self.salida_texto.insert("1.0", texto)

        except Exception as error:
            self.salida_texto.insert(
                "1.0",
                f"Error al ejecutar el método:\n{error}"
            )