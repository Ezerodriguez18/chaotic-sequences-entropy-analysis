# ===========================================================
# Generador de secuencia usando el mapa de tiendas
# Guarda los valores en un archivo de texto
# ===========================================================
from PyQt5 import QtWidgets
import sys
import struct
import numpy as np


# ============================================
# 1) MAPA 
# ============================================
def tent_map_sequence(u, x0, N, skip):
    x = x0
    for _ in range(skip):
        if x<u:
            x=x/u
        else:
            x=(1-x)/(1-u)
    seq = []
    for _ in range(N):
        if x<u:
            x=x/u
        else:
            x=(1-x)/(1-u)
        
        seq.append(x)
        #print(x)
    return seq


# ============================================
# 2) GUARDAR SECUENCIA DE FLOATS EN .TXT
# ============================================
def save_sequence_to_file(sequence, filename):
    with open(filename, "w") as f:
        for v in sequence:
            f.write(f"{v}\n") #un numero abajo de otro

# ============================================
# 3) EXPONENTE DE LYAPUNOV
# ============================================
def lyapunov_exponent_tent(u):
    """
    Lyapunov exponent for Tent Map.
    La secuencia no afecta el resultado, derivada absoluta constante.
    """
    return np.log(abs(u))


# ============================================
# 4) EXTRAER MANTISA (52 bits)
# ============================================
def get_mantissa_bits(x):
    bits64 = struct.unpack('>Q', struct.pack('>d', x))[0]
    mantissa = bits64 & ((1 << 52) - 1) # hace la and entre el numero en bits por tantos cerios y los 52 de la mantisa. << es corrimiento a la izquierda
    return mantissa


# ============================================
# 5) EXTRAER 26 BITS BAJOS
# ============================================
def lower_half_mantissa(m52):
    return m52 & ((1 << 26) - 1)# Lo mismo, extrae la mitad
def upper_half_mantissa(m52):
    return (m52 >> 26) & ((1 << 26) - 1)


# ============================================
# 6) MÉTODOS PARA GENERAR ¡UN BIT!
# ============================================

# Método A — Threshold a mitad del rango
def bit_method_A(n26):
    threshold = 1 << 25 # corrimiento hacia la izquierda 25 bits para hacer el umbral a la mitad
    return 1 if n26 > threshold else 0 

# Método B — LSB del entero
def bit_method_B(n26):
    return n26 & 1 #toma el lsb

# Método C — XOR de algunos bits
def bit_method_C(n26):
    b0  = (n26 >> 0) & 1
    b5  = (n26 >> 5) & 1
    b13 = (n26 >> 13) & 1
    b21 = (n26 >> 21) & 1
    return b0 ^ b5 ^ b13 ^ b21

# Método D — Von Neumann extractor (procesa lista entera)
def bits_method_D(n_list):
    bits = []
    for i in range(0, len(n_list) - 1, 2):
        a = n_list[i]
        b = n_list[i + 1]
        if a <= b:
            bits.append(1)
        elif a > b:
            bits.append(0)
        # si son iguales → descartar
    return bits  # <- asegurarse de que esté afuera del for
def bit_method_F(x):
    """
    Devuelve 1 si x >= 0.5
    Devuelve 0 si x < 0.5
    """
    return 1 if x >= 0.5 else 0


# ============================================
# 7) GUARDAR BITSTREAM EN .BIN
# ============================================
def save_bits_to_bin(bitlist, filename):
    with open(filename, "wb") as f:
        byte = 0
        count = 0
        for bit in bitlist:
            byte = (byte << 1) | bit
            count += 1
            if count == 8:
                f.write(byte.to_bytes(1, "big"))
                count = 0
                byte = 0

        if count > 0:  # completar byte final
            byte <<= (8 - count)
            f.write(byte.to_bytes(1, "big"))



def ask_file_dialog(default_name, filter_mask):
    """
    Abre un diálogo 'Guardar archivo'.
    Devuelve la ruta del archivo elegido o "" si se canceló.
    """
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
        None,
        "Guardar archivo",
        default_name,
        filter_mask
    )
    return filename

# ===========================================================
#  PROGRAMA PRINCIPAL
# ===========================================================
if __name__ == "__main__":# ejecuta solo si es codigo principal
    app = QtWidgets.QApplication(sys.argv)# sirve para los click y eventos del cuadro de dialogo

    # Parámetros
    u = 2/3
    x0 = 0.123456789   #X01
    
    N = 100_000_000   # Para NIST

    SKIP = 50000

    print("Generando secuencia de mapa de tienda...")
    seq = tent_map_sequence(u, x0, N, SKIP)

    print("Calculando exponente de Lyapunov...")
    lya = lyapunov_exponent_tent(u)
    print("Exponente de Lyapunov:", lya)

    # -------------------------------------------------------
    # Procesar mantisas
    # -------------------------------------------------------
    print("Extrayendo mantisas...")
    mantissas = [get_mantissa_bits(x) for x in seq]

    print("Tomando 26 bits bajos...")
    n26_list = [lower_half_mantissa(m) for m in mantissas]
    #n26_list = [upper_half_mantissa(m) for m in mantissas]

    print("Generando bits (Método..)…")
    bits = [bit_method_C(n) for n in n26_list]
    #bits = [bit_method_F(n) for n in n26_list]
    #bits = bits_method_D(n26_list) # para D
    print(f"Total de bits generados: {len(bits)}")
    bits_array = np.asarray(bits, dtype=np.uint8)

    count_ones = np.sum(bits_array == 1)
    count_zeros = np.sum(bits_array == 0)
    
    print("\n=== Estadísticas del bitstream ===")
    print("Cantidad de bits:", len(bits_array))
    print("Cantidad de 1s :", count_ones)
    print("Cantidad de 0s :", count_zeros)
    print("Proporción 1s  :", count_ones / len(bits_array))
    print("Proporción 0s  :", count_zeros / len(bits_array))
    print("Diferencia abs  :", abs(count_ones - count_zeros))
    print("=================================\n")
    # -------------------------------------------------------
    # Guardar para NIST (archivo binario)
    # -------------------------------------------------------
    archivo_nist = ask_file_dialog("tend_bits_nist.bin", 
                                   "Binary Files (*.bin);;All Files (*)")
    if archivo_nist:
        save_bits_to_bin(bits, archivo_nist)
        print("Bitstream NIST guardado en:", archivo_nist)


    print("\nFinalizado con éxito.")
