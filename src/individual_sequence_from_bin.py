import os
import sys
import random
import numpy as np
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)

# ========================================================
# Leer rango de bits de forma ultra rápida (NumPy)
# ========================================================
def read_binary_bit_range_fast(filename, bit_start, bit_count):
    """
    Lee bit_count bits a partir de bit_start (MSB-first) de forma rápida.
    """
    byte_start = bit_start // 8
    bit_offset = bit_start % 8
    bytes_to_read = (bit_offset + bit_count + 7) // 8

    with open(filename, "rb") as f:
        f.seek(byte_start)
        data = np.frombuffer(f.read(bytes_to_read), dtype=np.uint8)

    # Desempaqueta bytes a bits (MSB-first)
    bits = np.unpackbits(data)
    
    # Recorta el offset inicial y la cantidad requerida
    return bits[bit_offset : bit_offset + bit_count]


# ========================================================
# PROCESO PRINCIPAL
# ========================================================
def main():
    # 1. Seleccionar archivo de entrada
    archivo_entrada, _ = QtWidgets.QFileDialog.getOpenFileName(
        None,
        "Seleccionar archivo binario de origen",
        "",
        "Binary Files (*.bin *.bin.bin);;All Files (*)"
    )

    if not archivo_entrada:
        print("Operación cancelada. No se seleccionó archivo.")
        return

    # 2. Seleccionar la carpeta donde se guardarán los 50 archivos
    carpeta_destino = QtWidgets.QFileDialog.getExistingDirectory(
        None,
        "Seleccionar carpeta de destino para guardar las 50 secuencias"
    )

    if not carpeta_destino:
        print("Operación cancelada. No se seleccionó carpeta de destino.")
        return

    # 3. Parámetros de configuración
    DISCARD_BITS = 65536      # Ignorar al inicio y al final
    FPGA_BITS = 65536         # Tamaño de cada secuencia
    CANTIDAD_ARCHIVOS = 50    # Cantidad de secuencias a generar

    # Obtener tamaño total del archivo en bits
    bytes_totales = os.path.getsize(archivo_entrada)
    bits_totales = bytes_totales * 8

    print(f"Archivo cargado: {archivo_entrada}")
    print(f"Tamaño total: {bits_totales:,} bits ({bytes_totales:,} bytes)")

    # Rango válido para el inicio de la ventana deslizante:
    # Mínimo: descarte inicial (65536)
    # Máximo: total - descarte final (65536) - tamaño secuencia (65536)
    min_bit_inicio = DISCARD_BITS
    max_bit_inicio = bits_totales - DISCARD_BITS - FPGA_BITS

    if max_bit_inicio <= min_bit_inicio:
        print("Error: El archivo es demasiado chico para aplicar estas restricciones.")
        return

    print(f"\nGenerando {CANTIDAD_ARCHIVOS} secuencias desde posiciones de ventana deslizante aleatorias...")
    print(f"Rango de inicio permitido: Bit {min_bit_inicio:,} hasta Bit {max_bit_inicio:,}\n")

    # Generar 50 posiciones de inicio aleatorias (ventanas deslizantes)
    # Nota: Si querés que no se repita el inicio exacto, usamos random.sample o randint
    posiciones_inicio = [random.randint(min_bit_inicio, max_bit_inicio) for _ in range(CANTIDAD_ARCHIVOS)]

    # 4. Generar y guardar las 50 secuencias
    for i, bit_inicio in enumerate(posiciones_inicio, start=1):
        # Leer el bloque de 65536 bits desde la posición aleatoria
        bits_fpga = read_binary_bit_range_fast(archivo_entrada, bit_inicio, FPGA_BITS)

        # Nombre secuencial: secuencia_01.txt, secuencia_02.txt, ..., secuencia_50.txt
        nombre_archivo = f"secuencia_{i:02d}.txt"
        ruta_salida = os.path.join(carpeta_destino, nombre_archivo)

        # Guardar archivo formateado con bits separados por espacio
        with open(ruta_salida, "w") as f:
            f.write(" ".join(str(b) for b in bits_fpga))

        print(f"[{i:02d}/{CANTIDAD_ARCHIVOS}] Guardado '{nombre_archivo}' | Inicio en Bit: {bit_inicio:,}")

    print(f"\n¡Finalizado con éxito! Se guardaron los {CANTIDAD_ARCHIVOS} archivos en:")
    print(carpeta_destino)

if __name__ == "__main__":
    main()
