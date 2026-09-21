"""
corazon_i_love_you.py
Hecho por Michell (Annette Michell Valenzuela Rodriguez)

Idea: dibujar un corazon en la terminal usando puro texto "I love you",
que se va llenando poco a poco desde las orillas hacia el centro, y al
final deja el mensaje "I LOVE YOU" bien grande.

Nota para mi: si quiero que sea mas lento o mas rapido, solo cambio
FILL_DURATION y HOLD_DURATION mas abajo. Corre mejor haciendo doble
clic en abrir_corazon.bat en vez de meterlo desde Visual Studio.
"""

import os
import sys
import time

# ---- colores y utilerias de terminal (codigos ANSI) ----
ROJO = "\033[91m"
ROJO_NEGRITA = "\033[1;91m"
RESET = "\033[0m"
OCULTAR_CURSOR = "\033[?25l"
MOSTRAR_CURSOR = "\033[?25h"
# el \033[40m fuerza fondo negro aunque mi terminal tenga otro tema
LIMPIAR_PANTALLA = "\033[H\033[J\033[40m"

# ---- aqui controlo el tamano y la velocidad ----
ANCHO = 62              # columnas de la cuadricula
ALTO = 30                # renglones de la cuadricula
DURACION_LLENADO = 22.0    # segundos en llenarse el corazon (mas alto = mas lento)
DURACION_FINAL = 6.0       # segundos mostrando el mensaje final
TEXTO_PATRON = "I love you   "  # texto que se repite dentro del corazon


def construir_mascara_y_valores(ancho, alto):
    """
    Calculo, celda por celda, si cae dentro del corazon (usando la
    formula implicita del corazon) y de una vez guardo que tan
    'profundo' esta cada punto. Cerca de 0 = orilla, muy negativo =
    centro. Uso ese valor despues para decidir el orden en que se
    revela el dibujo (de orillas hacia el centro).
    """
    mascara = [[False] * ancho for _ in range(alto)]
    valores = [[0.0] * ancho for _ in range(alto)]
    for fila in range(alto):
        y = (alto / 2 - fila) / (alto / 2.2)
        for col in range(ancho):
            x = (col - ancho / 2) / (ancho / 2.6)
            valor = (x ** 2 + y ** 2 - 1) ** 3 - (x ** 2) * (y ** 3)
            valores[fila][col] = valor
            if valor <= 0:
                mascara[fila][col] = True
    return mascara, valores


def construir_tramos(mascara, valores):
    """
    Agrupo cada renglon en tramos continuos (para que siempre se vea
    la palabra completa y no una letra suelta) y calculo el promedio
    de 'profundidad' de cada tramo. Despues ordeno del mas cercano a
    la orilla al mas cercano al centro.
    """
    tramos = []
    for fila in range(ALTO):
        col = 0
        while col < ANCHO:
            if mascara[fila][col]:
                inicio = col
                while col < ANCHO and mascara[fila][col]:
                    col += 1
                fin = col
                promedio = sum(valores[fila][c] for c in range(inicio, fin)) / (fin - inicio)
                tramos.append((fila, inicio, fin, promedio))
            else:
                col += 1
    # de orilla (cerca de 0) a centro (muy negativo)
    tramos.sort(key=lambda t: t[3])
    return tramos


def dibujar_cuadro(mascara, revelado):
    """Arma el string completo de un cuadro de animacion."""
    lineas = []
    idx = 0
    for fila in range(ALTO):
        chars_fila = []
        for col in range(ANCHO):
            if mascara[fila][col]:
                ch = TEXTO_PATRON[idx % len(TEXTO_PATRON)]
                idx += 1
                if revelado[fila][col]:
                    chars_fila.append(f"{ROJO}{ch}{RESET}")
                else:
                    chars_fila.append(" ")
            else:
                chars_fila.append(" ")
        lineas.append("".join(chars_fila))
    return "\n".join(lineas)


# ---- letras de bloque, chiquitas, para el mensaje final ----
FUENTE = {
    "I": ["███", " █ ", " █ ", " █ ", "███"],
    "L": ["█   ", "█   ", "█   ", "█   ", "████"],
    "O": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "V": ["█   █", "█   █", "█   █", " █ █ ", "  █  "],
    "E": ["████", "█   ", "███ ", "█   ", "████"],
    "Y": ["█   █", " █ █ ", "  █  ", "  █  ", "  █  "],
    "U": ["█   █", "█   █", "█   █", "█   █", " ███ "],
    " ": ["  ", "  ", "  ", "  ", "  "],
}


def texto_grande(texto: str) -> str:
    """Convierto el mensaje final a letras de bloque, en rojo."""
    palabras = texto.split(" ")
    lineas = ["" for _ in range(5)]
    for i_palabra, palabra in enumerate(palabras):
        for letra in palabra:
            glifo = FUENTE.get(letra.upper(), FUENTE[" "])
            for li in range(5):
                lineas[li] += glifo[li] + " "
        if i_palabra != len(palabras) - 1:
            for li in range(5):
                lineas[li] += "   "
    return "\n".join(f"{ROJO_NEGRITA}{linea}{RESET}" for linea in lineas)


def main():
    # esto habilita que cmd.exe entienda los codigos de color en Windows
    os.system("")

    mascara, valores = construir_mascara_y_valores(ANCHO, ALTO)
    tramos = construir_tramos(mascara, valores)
    total_tramos = len(tramos)
    revelado = [[False] * ANCHO for _ in range(ALTO)]

    # no repinto en cada tramo (se ve muy brincado), sino cada ciertos pasos
    repintar_cada = max(1, total_tramos // 150)
    retraso_por_tramo = DURACION_LLENADO / total_tramos

    sys.stdout.write(OCULTAR_CURSOR)
    try:
        inicio = time.time()
        for i, (fila, col_inicio, col_fin, _valor) in enumerate(tramos):
            for c in range(col_inicio, col_fin):
                revelado[fila][c] = True

            if i % repintar_cada == 0 or i == total_tramos - 1:
                tiempo_meta = i * retraso_por_tramo
                transcurrido = time.time() - inicio
                if tiempo_meta > transcurrido:
                    time.sleep(tiempo_meta - transcurrido)
                sys.stdout.write(LIMPIAR_PANTALLA)
                sys.stdout.write(dibujar_cuadro(mascara, revelado))
                sys.stdout.flush()

        # ya se lleno completo, ahora pongo el mensaje grande abajo
        sys.stdout.write("\n\n")
        sys.stdout.write(texto_grande("I LOVE YOU"))
        sys.stdout.write("\n")
        sys.stdout.flush()

        time.sleep(DURACION_FINAL)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(MOSTRAR_CURSOR)
        sys.stdout.write(RESET + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
