import numpy as np
import matplotlib.pyplot as plt


# ========================================================
# --- Función para leer archivo .bin (igual que NIST) ---
# ========================================================
def read_binary_bitstream(filename):
    """Lee un archivo .bin y devuelve una lista de bits."""
    bits = []
    with open(filename, "rb") as f:
        data = f.read()
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
    return np.array(bits, dtype=np.uint8)
# ============================================================
#  FUNCIONES PARA ENTROPÍA DE BLOQUE / RATE ENTROPY
# ============================================================

def _words_from_bits(bits, W):
    bits = np.asarray(bits, dtype=np.uint8)
    N = len(bits)
    if N < W:
        raise ValueError(f"La longitud de la secuencia ({N}) es menor que W={W}.")

    mask = (1 << W) - 1
    words = np.empty(N - W + 1, dtype=np.int64)

    # primera palabra
    word = 0
    for i in range(W):
        word = (word << 1) | int(bits[i])
    words[0] = word

    # siguientes palabras
    for i in range(1, N - W + 1):
        word = ((word << 1) & mask) | int(bits[i + W - 1])
        words[i] = word

    return words


def block_entropy(bits, W):
    words = _words_from_bits(bits, W)
    counts = np.bincount(words, minlength=(1 << W))
    probs = counts[counts > 0] / counts.sum()
    S_W = -np.sum(probs * np.log2(probs))
    return S_W


def rate_entropy_h0(bits, W_max=20, alpha_min=10.0, verbose=False):
    """
    Devuelve:
      - W_values: W usados
      - S_W: entropía de bloque S_W
      - h_W: h(W) = S_{W+1} - S_W
      - h0_estimate: último h(W)
      - h0_from_SW: S_W / W del último W
    """
    bits = np.asarray(bits, dtype=np.uint8)
    N = len(bits)
    if N < 2:
        raise ValueError("La secuencia debe tener al menos 2 bits.")

    S_list = []
    W_list = []

    for W in range(1, W_max + 1):
        if N < W:
            break

        n_words = N - W + 1
        m = 1 << W
        alpha = n_words / m

        if verbose:
            print(f"W={W:2d}, alpha={alpha:8.3f}")

        if alpha < alpha_min:
            # cortamos cuando ya no hay buena estadística
            break

        S_W = block_entropy(bits, W)
        S_list.append(S_W)
        W_list.append(W)

    if len(S_list) < 2:
        raise ValueError("No hay suficientes W válidos para estimar h0.")

    S_arr = np.array(S_list)
    W_arr = np.array(W_list)
    h_arr = S_arr[1:] - S_arr[:-1]

    h0_estimate = h_arr[-1]          # h(Wmax)
    h0_from_SW = S_arr[-1] / W_arr[-1]

    return {
        "W_values": W_arr,
        "S_W": S_arr,
        "h_W": h_arr,
        "h0_estimate": h0_estimate,
        "h0_from_SW": h0_from_SW,
    }


# ============================================================
#   DEMO: RAND vs SECUENCIA PERIÓDICA
# ============================================================

if __name__ == "__main__":
    N = 1_000_000
    W_max = 18
    alpha_min = 10.0

    # =========================================
    # 1) TU ARCHIVO DEL MAPA LOGÍSTICO
    # =========================================
    archivo = "secuencia100M_secuencial.bin"   # <-- CAMBIÁ EL QUE QUIERAS
    bits_log = read_binary_bitstream(archivo)
    bits_log = bits_log[:N]
    # recorto a N bits por igualdad con el random
    res_log = rate_entropy_h0(bits_log, W_max=W_max, alpha_min=alpha_min)
    
    # 2) Secuencia periódica
    #    Por ejemplo, patrón '01011010' (periodo 8)
    pattern = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.uint8)
    bits_per = np.resize(pattern, N)  # repetir patrón hasta longitud N

    res_per = rate_entropy_h0(bits_per, W_max=W_max, alpha_min=alpha_min)
    print("=== SECUENCIA PERIÓDICA ===")
    print("W usados:", res_per["W_values"])
    print("h(W) =", res_per["h_W"])
    print("h0_estimate (último h(W)) =", res_per["h0_estimate"])
    print("h0_from_SW (S_W/W)        =", res_per["h0_from_SW"])

    # =======================================================
    #  Gráficos comparativos S_W vs W y h(W) vs W
    # =======================================================
    W_r = res_log["W_values"]
    S_r = res_log["S_W"]
    h_r = res_log["h_W"]
    
    W_r = res_rand["W_values"]
    S_r = res_rand["S_W"]
    h_r = res_rand["h_W"]

    W_p = res_per["W_values"]
    S_p = res_per["S_W"]
    h_p = res_per["h_W"]

    # S_W vs W
    plt.figure()
    plt.plot(W_r, S_r, 'o-', label='Aleatoria')
    plt.plot(W_p, S_p, 's--', label='Periódica')
    plt.xlabel("W")
    plt.ylabel("S_W (bits)")
    plt.title("Entropía de bloque S_W vs W")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # h(W) vs W
    plt.figure()
    plt.plot(W_r[1:], h_r, 'o-', label='Aleatoria')
    plt.plot(W_p[1:], h_p, 's--', label='Periódica')
    plt.xlabel("W")
    plt.ylabel("h(W) = S_{W+1} - S_W (bits/símbolo)")
    plt.title("Entropía diferencial h(W) vs W")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
