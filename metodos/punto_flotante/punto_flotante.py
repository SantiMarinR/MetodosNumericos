import math

from core.metodo_base import MetodoNumerico
from core.resultado import ResultadoMetodo


class PuntoFlotante(MetodoNumerico):
    nombre = "Punto flotante"
    categoria = "Punto flotante"
    descripcion = "Representación de números en punto flotante usando signo, exponente y mantisa."

    parametros = []

    # =========================================================
    # VALIDACIONES
    # =========================================================

    def validar_configuracion(self, total_bits, bits_signo, bits_exponente, bits_mantisa):
        total_bits = int(total_bits)
        bits_signo = int(bits_signo)
        bits_exponente = int(bits_exponente)
        bits_mantisa = int(bits_mantisa)

        if total_bits <= 0:
            raise ValueError("La cantidad total de bits debe ser mayor que cero.")

        if bits_signo != 1:
            raise ValueError("Para este programa el signo debe ocupar exactamente 1 bit.")

        if bits_exponente <= 0:
            raise ValueError("Los bits del exponente deben ser mayores que cero.")

        if bits_mantisa <= 0:
            raise ValueError("Los bits de la mantisa deben ser mayores que cero.")

        suma = bits_signo + bits_exponente + bits_mantisa

        if suma != total_bits:
            raise ValueError(
                f"La suma no coincide: signo({bits_signo}) + exponente({bits_exponente}) "
                f"+ mantisa({bits_mantisa}) = {suma}, pero el total indicado es {total_bits}."
            )

        return total_bits, bits_signo, bits_exponente, bits_mantisa

    # =========================================================
    # FUNCIONES AUXILIARES
    # =========================================================

    def entero_a_binario(self, valor, ancho):
        if valor < 0 or valor >= 2 ** ancho:
            raise ValueError(
                f"El valor {valor} no cabe en {ancho} bits de exponente."
            )

        return list(format(valor, f"0{ancho}b"))

    def fraccion_a_bits(self, fraccion, cantidad_bits, redondear=False):
        bits = []
        valor = fraccion

        limite = cantidad_bits + 1 if redondear else cantidad_bits

        for _ in range(limite):
            valor *= 2

            if valor >= 1:
                bits.append("1")
                valor -= 1
            else:
                bits.append("0")

        acarreo = False

        if redondear and len(bits) > cantidad_bits:
            bit_guardia = bits[-1]
            bits = bits[:-1]

            if bit_guardia == "1":
                numero = int("".join(bits), 2) if bits else 0
                numero += 1

                if numero >= 2 ** cantidad_bits:
                    bits = list("0" * cantidad_bits)
                    acarreo = True
                else:
                    bits = list(format(numero, f"0{cantidad_bits}b"))

        return bits, acarreo

    def valor_mantisa(self, bits_mantisa):
        valor = 1.0

        for posicion, bit in enumerate(bits_mantisa, start=1):
            if bit == "1":
                valor += 2 ** (-posicion)

        return valor

    def bits_a_entero(self, bits):
        return int("".join(bits), 2) if bits else 0

    # =========================================================
    # OPCION 1: DECIMAL A N.P.F.
    # =========================================================

    def decimal_a_npf(self, numero, total_bits, bits_signo, bits_exponente, bits_mantisa, modo):
        total_bits, bits_signo, bits_exponente, bits_mantisa = self.validar_configuracion(
            total_bits,
            bits_signo,
            bits_exponente,
            bits_mantisa
        )

        numero = float(numero)
        modo = str(modo)

        bit_signo = "1" if numero < 0 else "0"
        signo_valor = -1 if bit_signo == "1" else 1

        sesgo = (2 ** (bits_exponente - 1)) - 1

        if numero == 0:
            bits_exp = list("0" * bits_exponente)
            bits_man = list("0" * bits_mantisa)

            return self.armar_respuesta(
                bits_signo=[bit_signo],
                bits_exponente=bits_exp,
                bits_mantisa=bits_man,
                signo_valor=signo_valor,
                exponente_real=0,
                exponente_sesgado=0,
                sesgo=sesgo,
                mantisa_valor=0,
                valor_decimal=0,
                modo=modo,
                pasos=[
                    "El número ingresado es cero.",
                    "El exponente y la mantisa se representan con ceros."
                ]
            )

        numero_abs = abs(numero)

        exponente_real = math.floor(math.log(numero_abs, 2))
        mantisa_real = numero_abs / (2 ** exponente_real)
        fraccion_mantisa = mantisa_real - 1

        redondear = "IEEE" in modo.upper()

        bits_man, acarreo = self.fraccion_a_bits(
            fraccion_mantisa,
            bits_mantisa,
            redondear=redondear
        )

        if acarreo:
            exponente_real += 1

        exponente_sesgado = exponente_real + sesgo
        bits_exp = self.entero_a_binario(exponente_sesgado, bits_exponente)

        mantisa_guardada = self.valor_mantisa(bits_man)
        valor_decimal = signo_valor * mantisa_guardada * (2 ** exponente_real)

        pasos = [
            f"Se toma el valor absoluto: |{numero}| = {numero_abs}.",
            f"Se normaliza: {numero_abs} = {mantisa_real:.10f} × 2^{exponente_real}.",
            f"Bit de signo: {bit_signo}.",
            f"Sesgo del exponente: 2^({bits_exponente}-1) - 1 = {sesgo}.",
            f"Característica: {exponente_real} + {sesgo} = {exponente_sesgado}.",
            f"Exponente en binario: {''.join(bits_exp)}.",
            f"Mantisa almacenada: {''.join(bits_man)}.",
        ]

        if redondear:
            pasos.append("Modo IEEE 754 / normalizada: la mantisa se redondea.")
        else:
            pasos.append("Modo representación simple: la mantisa se trunca.")

        return self.armar_respuesta(
            bits_signo=[bit_signo],
            bits_exponente=bits_exp,
            bits_mantisa=bits_man,
            signo_valor=signo_valor,
            exponente_real=exponente_real,
            exponente_sesgado=exponente_sesgado,
            sesgo=sesgo,
            mantisa_valor=mantisa_guardada,
            valor_decimal=valor_decimal,
            modo=modo,
            pasos=pasos
        )

    # =========================================================
    # OPCION 2: N.P.F. A DECIMAL
    # =========================================================

    def npf_a_decimal(self, bits, total_bits, bits_signo, bits_exponente, bits_mantisa, modo):
        total_bits, bits_signo, bits_exponente, bits_mantisa = self.validar_configuracion(
            total_bits,
            bits_signo,
            bits_exponente,
            bits_mantisa
        )

        bits = [str(bit).strip() for bit in bits]

        if len(bits) != total_bits:
            raise ValueError(f"Debes ingresar exactamente {total_bits} bits.")

        for bit in bits:
            if bit not in ["0", "1"]:
                raise ValueError("Los bits solo pueden ser 0 o 1.")

        grupo_signo = bits[:bits_signo]
        grupo_exponente = bits[bits_signo:bits_signo + bits_exponente]
        grupo_mantisa = bits[bits_signo + bits_exponente:]

        bit_signo = grupo_signo[0]
        signo_valor = -1 if bit_signo == "1" else 1

        sesgo = (2 ** (bits_exponente - 1)) - 1

        exponente_sesgado = self.bits_a_entero(grupo_exponente)
        exponente_real = exponente_sesgado - sesgo

        mantisa_valor = self.valor_mantisa(grupo_mantisa)

        if exponente_sesgado == 0 and set(grupo_mantisa) == {"0"}:
            valor_decimal = 0
            mantisa_valor = 0
            exponente_real = 0
        else:
            valor_decimal = signo_valor * mantisa_valor * (2 ** exponente_real)

        pasos = [
            f"Bit de signo: {bit_signo}.",
            f"Exponente en bits: {''.join(grupo_exponente)} = {exponente_sesgado}.",
            f"Sesgo: 2^({bits_exponente}-1) - 1 = {sesgo}.",
            f"Exponente real: {exponente_sesgado} - {sesgo} = {exponente_real}.",
            f"Mantisa: {mantisa_valor:.10f}.",
            f"Valor decimal: {signo_valor} × {mantisa_valor:.10f} × 2^{exponente_real} = {valor_decimal:.10f}.",
        ]

        return self.armar_respuesta(
            bits_signo=grupo_signo,
            bits_exponente=grupo_exponente,
            bits_mantisa=grupo_mantisa,
            signo_valor=signo_valor,
            exponente_real=exponente_real,
            exponente_sesgado=exponente_sesgado,
            sesgo=sesgo,
            mantisa_valor=mantisa_valor,
            valor_decimal=valor_decimal,
            modo=modo,
            pasos=pasos
        )

    # =========================================================
    # ARMADO DE RESPUESTA
    # =========================================================

    def armar_respuesta(
        self,
        bits_signo,
        bits_exponente,
        bits_mantisa,
        signo_valor,
        exponente_real,
        exponente_sesgado,
        sesgo,
        mantisa_valor,
        valor_decimal,
        modo,
        pasos
    ):
        bits = bits_signo + bits_exponente + bits_mantisa

        if valor_decimal == 0:
            formula = "0"
        else:
            formula = f"{signo_valor} × {mantisa_valor:.10f} × 2^{exponente_real}"

        return {
            "bits": bits,
            "bits_texto": "".join(bits),
            "bits_signo": bits_signo,
            "bits_exponente": bits_exponente,
            "bits_mantisa": bits_mantisa,
            "signo_valor": signo_valor,
            "exponente_real": exponente_real,
            "exponente_sesgado": exponente_sesgado,
            "sesgo": sesgo,
            "mantisa_valor": mantisa_valor,
            "valor_decimal": valor_decimal,
            "formula": formula,
            "modo": modo,
            "pasos": pasos,
        }

    def ejecutar(self, **kwargs):
        return ResultadoMetodo(
            resultado=None,
            mensaje="Este método usa una pantalla especial con dos opciones.",
            pasos=[],
            tabla=[]
        )