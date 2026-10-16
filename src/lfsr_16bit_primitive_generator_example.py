import numpy as np

def generate_lfsr_16bit_bin(n_bits, filename):
    print(f"Generando secuencia LFSR de {n_bits:,} bits...")
    
    state = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0], dtype=np.uint8)
    
    sequence = np.empty(n_bits, dtype=np.uint8)
    
    for i in range(n_bits):
        output = state[15]
        sequence[i] = output
        
        # Cálculo del bit de realimentación (feedback) usando los taps: 15, 14, 12, 3
        feedback = state[15] ^ state[14] ^ state[12] ^ state[3]
        
        # Desplazamiento hacia la derecha e inserción del feedback al inicio
        state[1:] = state[:-1]
        state[0] = feedback

    # Guardar directamente en formato binario (.bin)
    with open(filename, 'wb') as f:
        f.write(sequence.tobytes())
        
    print(f"Secuencia guardada exitosamente en '{filename}'")

# Ejemplo de uso para 100 millones de bits
generate_lfsr_16bit_bin(100_000_000, 'secuencia_lfsr_100M.bin')
