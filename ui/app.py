import customtkinter as ctk

from core.registro import obtener_metodos


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Proyecto de Métodos Numéricos")
        self.geometry("1200x720")
        self.minsize(1000, 650)

        self.metodos_clases = obtener_metodos()
        self.metodos_por_categoria = self.agrupar_metodos()

        self.categoria_actual = None
        self.metodo_actual = None
        self.entradas = {}

        self.crear_interfaz()

    def agrupar_metodos(self):
        datos = {}

        for clase in self.metodos_clases:
            categoria = clase.categoria

            if categoria not in datos:
                datos[categoria] = []

            datos[categoria].append(clase)

        for categoria in datos:
            datos[categoria].sort(key=lambda clase: clase.nombre)

        return dict(sorted(datos.items()))

    def crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        # =========================
        # ENCABEZADO
        # =========================

        encabezado = ctk.CTkFrame(self, corner_radius=0, fg_color="#1f3c88")
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
        encabezado.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            encabezado,
            text="Proyecto de Métodos Numéricos",
            font=("Arial", 30, "bold"),
            text_color="white"
        )
        titulo.grid(row=0, column=0, padx=25, pady=(18, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            encabezado,
            text="Python · Programación Orientada a Objetos · App de escritorio",
            font=("Arial", 15),
            text_color="#dbe6ff"
        )
        subtitulo.grid(row=1, column=0, padx=25, pady=(0, 18), sticky="w")

        # =========================
        # PANEL IZQUIERDO
        # =========================

        self.panel_izquierdo = ctk.CTkFrame(self, fg_color="#eef2ff", corner_radius=18)
        self.panel_izquierdo.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.panel_izquierdo.grid_columnconfigure(0, weight=1)

        label_categoria = ctk.CTkLabel(
            self.panel_izquierdo,
            text="1. Selecciona una categoría",
            font=("Arial", 18, "bold"),
            text_color="#1f3c88"
        )
        label_categoria.grid(row=0, column=0, padx=18, pady=(25, 8), sticky="w")

        categorias = list(self.metodos_por_categoria.keys())

        self.selector_categoria = ctk.CTkOptionMenu(
            self.panel_izquierdo,
            values=categorias,
            command=self.cambiar_categoria,
            height=38,
            font=("Arial", 14)
        )
        self.selector_categoria.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="ew")

        label_metodo = ctk.CTkLabel(
            self.panel_izquierdo,
            text="2. Selecciona un método",
            font=("Arial", 18, "bold"),
            text_color="#1f3c88"
        )
        label_metodo.grid(row=2, column=0, padx=18, pady=(10, 8), sticky="w")

        self.selector_metodo = ctk.CTkOptionMenu(
            self.panel_izquierdo,
            values=["Selecciona una categoría"],
            command=self.cambiar_metodo,
            height=38,
            font=("Arial", 14)
        )
        self.selector_metodo.grid(row=3, column=0, padx=18, pady=(0, 18), sticky="ew")

        label_info = ctk.CTkLabel(
            self.panel_izquierdo,
            text="Información del método",
            font=("Arial", 18, "bold"),
            text_color="#1f3c88"
        )
        label_info.grid(row=4, column=0, padx=18, pady=(12, 8), sticky="w")

        self.info_metodo = ctk.CTkTextbox(
            self.panel_izquierdo,
            height=190,
            wrap="word",
            corner_radius=12
        )
        self.info_metodo.grid(row=5, column=0, padx=18, pady=(0, 18), sticky="nsew")

        self.panel_izquierdo.grid_rowconfigure(5, weight=1)

        instrucciones = ctk.CTkLabel(
            self.panel_izquierdo,
            text="Cada equipo edita solamente su archivo dentro de la carpeta metodos/.",
            font=("Arial", 13),
            text_color="#555",
            wraplength=330,
            justify="left"
        )
        instrucciones.grid(row=6, column=0, padx=18, pady=(0, 25), sticky="w")

        # =========================
        # PANEL DERECHO
        # =========================

        self.panel_derecho = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.panel_derecho.grid(row=1, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.panel_derecho.grid_columnconfigure(0, weight=1)
        self.panel_derecho.grid_rowconfigure(5, weight=1)

        self.titulo_metodo = ctk.CTkLabel(
            self.panel_derecho,
            text="Selecciona un método",
            font=("Arial", 26, "bold"),
            text_color="#1f3c88"
        )
        self.titulo_metodo.grid(row=0, column=0, padx=25, pady=(25, 6), sticky="w")

        self.descripcion_metodo = ctk.CTkLabel(
            self.panel_derecho,
            text="Aquí aparecerán los campos necesarios para calcular.",
            font=("Arial", 14),
            text_color="#555",
            wraplength=760,
            justify="left"
        )
        self.descripcion_metodo.grid(row=1, column=0, padx=25, pady=(0, 16), sticky="w")

        self.frame_formulario = ctk.CTkScrollableFrame(
            self.panel_derecho,
            height=190,
            corner_radius=14,
            fg_color="#f6f8fc"
        )
        self.frame_formulario.grid(row=2, column=0, padx=25, pady=(0, 15), sticky="ew")
        self.frame_formulario.grid_columnconfigure(0, weight=1)

        self.boton_calcular = ctk.CTkButton(
            self.panel_derecho,
            text="Calcular",
            command=self.calcular,
            height=42,
            font=("Arial", 16, "bold"),
            fg_color="#1f3c88",
            hover_color="#162b63"
        )
        self.boton_calcular.grid(row=3, column=0, padx=25, pady=(0, 18), sticky="w")

        label_salida = ctk.CTkLabel(
            self.panel_derecho,
            text="Resultado",
            font=("Arial", 21, "bold"),
            text_color="#1f3c88"
        )
        label_salida.grid(row=4, column=0, padx=25, pady=(0, 8), sticky="w")

        self.salida_texto = ctk.CTkTextbox(
            self.panel_derecho,
            wrap="word",
            corner_radius=14,
            font=("Consolas", 13)
        )
        self.salida_texto.grid(row=5, column=0, padx=25, pady=(0, 25), sticky="nsew")

        if categorias:
            self.selector_categoria.set(categorias[0])
            self.cambiar_categoria(categorias[0])

    def cambiar_categoria(self, categoria):
        self.categoria_actual = categoria

        clases = self.metodos_por_categoria[categoria]
        nombres = [clase.nombre for clase in clases]

        self.selector_metodo.configure(values=nombres)

        if nombres:
            self.selector_metodo.set(nombres[0])
            self.cambiar_metodo(nombres[0])

    def cambiar_metodo(self, nombre_metodo):
        clases = self.metodos_por_categoria[self.categoria_actual]

        clase_seleccionada = None

        for clase in clases:
            if clase.nombre == nombre_metodo:
                clase_seleccionada = clase
                break

        if clase_seleccionada is None:
            return

        self.metodo_actual = clase_seleccionada()

        self.titulo_metodo.configure(text=self.metodo_actual.nombre)
        self.descripcion_metodo.configure(text=self.metodo_actual.descripcion)

        self.info_metodo.configure(state="normal")
        self.info_metodo.delete("1.0", "end")
        self.info_metodo.insert(
            "1.0",
            f"Nombre:\n{self.metodo_actual.nombre}\n\n"
            f"Categoría:\n{self.metodo_actual.categoria}\n\n"
            f"Descripción:\n{self.metodo_actual.descripcion}"
        )
        self.info_metodo.configure(state="disabled")

        self.construir_formulario()

        self.salida_texto.delete("1.0", "end")
        self.salida_texto.insert(
            "1.0",
            "Llena los parámetros y presiona Calcular."
        )

    def construir_formulario(self):
        for widget in self.frame_formulario.winfo_children():
            widget.destroy()

        self.entradas = {}

        if not self.metodo_actual.parametros:
            aviso = ctk.CTkLabel(
                self.frame_formulario,
                text="Este método todavía no tiene parámetros definidos.\nEdita su archivo dentro de la carpeta metodos/.",
                font=("Arial", 15),
                text_color="#7a5a00",
                justify="left"
            )
            aviso.grid(row=0, column=0, padx=15, pady=18, sticky="w")
            return

        for i, parametro in enumerate(self.metodo_actual.parametros):
            label = ctk.CTkLabel(
                self.frame_formulario,
                text=parametro.get("label", parametro.get("nombre", "Parámetro")),
                font=("Arial", 14, "bold"),
                text_color="#333"
            )
            label.grid(row=i * 2, column=0, padx=15, pady=(12, 3), sticky="w")

            entrada = ctk.CTkEntry(
                self.frame_formulario,
                placeholder_text=parametro.get("placeholder", ""),
                height=36,
                font=("Arial", 14)
            )
            entrada.grid(row=i * 2 + 1, column=0, padx=15, pady=(0, 8), sticky="ew")

            self.entradas[parametro["nombre"]] = entrada

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

            if not resultado.pasos and not resultado.tabla and resultado.resultado is None:
                texto += "Este método todavía no devuelve cálculos.\n"

            self.salida_texto.insert("1.0", texto)

        except Exception as error:
            self.salida_texto.insert(
                "1.0",
                f"Error al ejecutar el método:\n{error}"
            )