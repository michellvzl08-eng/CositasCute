"""
Animación de corazón formado por texto "I love you" en rojo.
Se va llenando progresivamente durante ~15-20 segundos y al final
muestra el mensaje "I LOVE YOU" en grande.

Requiere una terminal que soporte códigos ANSI (la mayoría lo hacen:
Linux, macOS, Windows Terminal / PowerShell moderno).
"""

import os
import sys
import time
import random

# --- Colores ANSI ---
RED = "\033[91m"
BOLD_RED = "\033[1;91m"
RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_HOME = "\033[H\033[J"

# --- Configuración ---
WIDTH = 60          # ancho de la cuadrícula
HEIGHT = 30          # alto de la cuadrícula
FILL_DURATION = 14.0   # segundos para llenar el corazón
HOLD_DURATION = 5.0    # segundos mostrando el mensaje final
PATTERN_TEXT = "I love you "  # texto que "fluye" dentro del corazón


def build_heart_mask(width: int, height: int):
    """Genera una máscara booleana con forma de corazón."""
    mask = [[False] * width for _ in range(height)]
    for row in range(height):
        # y va de arriba (positivo) hacia abajo (negativo)
        y = (height / 2 - row) / (height / 2.2)
        for col in range(width):
            x = (col - width / 2) / (width / 2.6)
            value = (x ** 2 + y ** 2 - 1) ** 3 - (x ** 2) * (y ** 3)
            if value <= 0:
                mask[row][col] = True
    return mask


def render_frame(mask, revealed):
    """Construye el string completo de un frame."""
    lines = []
    idx = 0
    for row in range(HEIGHT):
        line_chars = []
        for col in range(WIDTH):
            if mask[row][col]:
                ch = PATTERN_TEXT[idx % len(PATTERN_TEXT)]
                idx += 1
                if revealed[row][col]:
                    line_chars.append(f"{RED}{ch}{RESET}")
                else:
                    line_chars.append(" ")
            else:
                line_chars.append(" ")
        lines.append("".join(line_chars))
    return "\n".join(lines)


def final_message():
    """Mensaje grande final, hecho con bloques simples."""
    banner = [
        r"  _____   _                            __     __            ",
        r" |_   _| | |    ___ __   __  ___       \ \   / /  ___   _   _ ",
        r"   | |   | |   / _ \\ \ / / / _ \       \ \ / /  / _ \ | | | |",
        r"   | |   | |  | (_) |\ V / | __/        \ V /  | (_) || |_| |",
        r"   |_|   |_|   \___/  \_/   \___|         \_/    \___/  \__,_|",
    ]
    return "\n".join(f"{BOLD_RED}{line}{RESET}" for line in banner)


def main():
    mask = build_heart_mask(WIDTH, HEIGHT)
    cells = [(r, c) for r in range(HEIGHT) for c in range(WIDTH) if mask[r][c]]
    random.shuffle(cells)

    revealed = [[False] * WIDTH for _ in range(HEIGHT)]
    total_cells = len(cells)

    sys.stdout.write(HIDE_CURSOR)
    try:
        start = time.time()
        for i, (r, c) in enumerate(cells):
            revealed[r][c] = True
            # Repinta cada cierto número de celdas para no saturar la terminal
            if i % max(1, total_cells // 200) == 0:
                elapsed = time.time() - start
                target_time = (i / total_cells) * FILL_DURATION
                if target_time > elapsed:
                    time.sleep(target_time - elapsed)
                sys.stdout.write(CLEAR_HOME)
                sys.stdout.write(render_frame(mask, revealed))
                sys.stdout.flush()

        # Frame final del corazón completo
        sys.stdout.write(CLEAR_HOME)
        sys.stdout.write(render_frame(mask, revealed))
        sys.stdout.write("\n\n")
        sys.stdout.write(final_message())
        sys.stdout.flush()

        time.sleep(HOLD_DURATION)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(RESET + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
