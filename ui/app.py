import unicodedata

import customtkinter as ctk

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