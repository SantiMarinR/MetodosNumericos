import unicodedata

import numpy as np
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
            "Diferencia dividida adelante",
            "Diferencia dividida atrás",
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