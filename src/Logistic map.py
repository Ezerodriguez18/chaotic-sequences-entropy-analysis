# ===========================================================
# Generador de secuencia usando el mapa logístico
# Guarda los valores en un archivo de texto
# ===========================================================
from PyQt5 import QtWidgets
import sys
import struct
import numpy as np
app = QtWidgets.QApplication(sys.argv)

# ============================================
# 1) MAPA LOGÍSTICO
# ============================================
def logistic_map_sequence(r, x0, N, skip):
    x = x0
    for _ in range(skip):
        x = r * x * (1 - x)

    seq = []
    for _ in range(N):
        x = r * x * (1 - x)
        seq.append(x)
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
def lyapunov_exponent(r, x_sequence):
    x_sequence = np.array(x_sequence)
    eps = 1e-8
    deriv = np.abs(r * (1 - 2 * x_sequence)) + eps #derivada
    return np.mean(np.log(deriv))# devuelve el la media, osea el valor de lyapunov


# ============================================
# 4) EXTRAER MANTISA (52 bits)
# ============================================
def get_mantissa_bits(x):
    bits64 = struct.unpack('>Q', struct.pack('>d', x))[0]
    mantissa = bits64 & ((1 << 52) - 1) 
    return mantissa


# ============================================
# 5) EXTRAER 26 BITS BAJOS
# ============================================
def lower_half_mantissa(m52):
    return m52 & ((1 << 26) - 1)
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
    return bits  
  
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
    # Parámetros
    r = 4.0
    x0 = 0.123456789
    
    N = 100_000_000   # Para NIST con 100_000_000
   # N = 200_000_000   # Para metodo D
    SKIP = 0
    FPGA_BITS = 65536

    print("Generando secuencia logística...")
    seq = logistic_map_sequence(r, x0, N, SKIP)

     print("Calculando exponente de Lyapunov...")
     lya = lyapunov_exponent(r, seq)
     print("Exponente de Lyapunov:", lya)

    # -------------------------------------------------------
    # Guardar archivo de floats
    # -------------------------------------------------------
    archivo_floats = ask_file_dialog("logistic_sequence.txt", 
                                     "Text Files (*.txt);;All Files (*)")
    if archivo_floats:
        save_sequence_to_file(seq, archivo_floats)
        print("Floats guardados en:", archivo_floats)

    # -------------------------------------------------------
    # Procesar mantisas
    # -------------------------------------------------------
    print("Extrayendo mantisas...")
    mantissas = [get_mantissa_bits(x) for x in seq]

    print("Tomando 26 bits bajos...")
    #n26_list = [upper_half_mantissa(m) for m in mantissas]
    n26_list = [lower_half_mantissa(m) for m in mantissas]

    print("Generando bits (Método..)…")
    #bits = [bit_method_F(n) for n in seq]
    #bits = [bit_method_C(n) for n in n26_list]
    #bits = [bit_method_A(n) for n in n26_list]
    #bits = [bit_method_B(n) for n in n26_list]
    
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
    archivo_nist = ask_file_dialog("rng_bits_nist.bin", 
                                   "Binary Files (*.bin);;All Files (*)")
    if archivo_nist:
        save_bits_to_bin(bits, archivo_nist)
        print("Bitstream NIST guardado en:", archivo_nist)


    print("\nFinalizado con éxito.")
