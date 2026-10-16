# ==========================================================
# Generación de secuencias de 100 millones de bits
# 1) Estilo MATLAB randi([0,1]) -> usando NumPy
# 2) Criptográfico -> usando secrets
# Guarda cada secuencia en un archivo .bin para NIST
# Además, calcula cantidad de 0s y 1s.
# ==========================================================

import numpy as np
import secrets

# ----------------------------------------------------------
# Parámetros
# ----------------------------------------------------------
N_BITS = 1_000_000_000
OUTPUT_RANDI = "matlab_randi_like_1G.bin"
OUTPUT_SECRETS = "secrets_1G.bin"


# ----------------------------------------------------------
# 1) Estilo MATLAB randi([0,1])
# ----------------------------------------------------------
def generate_randi_like(n_bits, filename):
    print("Generando secuencia estilo MATLAB randi([0,1])...")

    rng = np.random.default_rng()

    # Generar valores 0/1 directamente
    bits = rng.integers(0, 2, size=n_bits, dtype=np.uint8)

    # -------------------------------
    # Conteo de ceros y unos
    # -------------------------------
    count_ones = int(bits.sum())
    count_zeros = n_bits - count_ones

    print(f"  → Unos  : {count_ones}")
    print(f"  → Ceros : {count_zeros}")
    print(f"  → Proporción de 1s = {count_ones / n_bits:.6f}")
    print(f"  → Proporción de 0s = {count_zeros / n_bits:.6f}")

    # Empaquetar a bytes (8 bits → 1 byte)
    packed = np.packbits(bits)

    print("Guardando archivo:", filename)
    with open(filename, "wb") as f:
        f.write(packed)

    print("Listo estilo randi.\n")


# ----------------------------------------------------------
# 2) Generador criptográfico con secrets
# ----------------------------------------------------------
def generate_secrets(n_bits, filename):
    print("Generando secuencia criptográfica (secrets)...")

    n_bytes = (n_bits + 7) // 8
    data = bytearray(n_bytes)

    for i in range(n_bytes):
        data[i] = secrets.randbits(8)

    # -------------------------------
    # Conteo de ceros y unos
    # -------------------------------
    # Expandir los bytes a bits
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

    # Recortar por si sobran bits (cuando n_bits no es múltiplo de 8)
    bits = bits[:n_bits]

    count_ones = int(bits.sum())
    count_zeros = n_bits - count_ones

    print(f"  → Unos  : {count_ones}")
    print(f"  → Ceros : {count_zeros}")
    print(f"  → Proporción de 1s = {count_ones / n_bits:.6f}")
    print(f"  → Proporción de 0s = {count_zeros / n_bits:.6f}")

    print("Guardando archivo:", filename)
    with open(filename, "wb") as f:
        f.write(data)

    print("Listo cryptográfico.\n")


# ----------------------------------------------------------
# Ejecución principal
# ----------------------------------------------------------
if __name__ == "__main__":
    generate_randi_like(N_BITS, OUTPUT_RANDI)
    generate_secrets(N_BITS, OUTPUT_SECRETS)

    print("=== Finalizado ===")
    print("Archivos generados:\n -", OUTPUT_RANDI, "\n -", OUTPUT_SECRETS)
