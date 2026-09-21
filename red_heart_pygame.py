"""
red_heart_pygame.py
Hecho por Michell (Annette Michell Valenzuela Rodriguez)

Version "bonita" del corazon, con ventana grafica de verdad usando
pygame en vez de puro texto en consola. Vi un ejemplo parecido hecho
en azul y lo reescribi con mi paleta de rojos, agregando el efecto
de brillo (glow) alrededor de cada palabra.

Como correrlo:
    pip install pygame
    python red_heart_pygame.py

O directo con doble clic en abrir_corazon_pygame.bat, que ya se
encarga de instalar pygame si me hace falta.

Tip para mi: si quiero musica de fondo, solo pongo un archivo
llamado "musica.mp3" en esta misma carpeta y se reproduce solo.
"""

import math
import os
import random

import pygame

# ---- configuracion general ----
ANCHO, ALTO = 1000, 700
FPS = 60
ESCALA = 20
COLOR_FONDO = (0, 0, 0)

PALABRAS = ["love you", "Love You", "LOVE YOU"]
TEXTO_CENTRAL = " I Love You "

# mi paleta de rojos, de mas apagado a mas vivo
PALETA_ROJOS = [
    (178, 34, 34),    # firebrick
    (220, 20, 60),    # crimson
    (255, 0, 0),      # rojo puro
    (200, 30, 45),
    (139, 0, 0),      # dark red
]

ARCHIVO_MUSICA = "musica.mp3"  # opcional, si no existe no truena nada


class Particula:
    """Cada palabrita que aparece en el corazon es una de estas."""
    __slots__ = (
        "x", "y", "orden", "tipo", "palabra", "color",
        "alfa", "parpadeo", "fuente", "retraso", "escala_extra",
    )

    def __init__(self, x, y, orden, tipo):
        self.x = x
        self.y = y
        self.orden = orden
        self.tipo = tipo
        self.palabra = random.choice(PALABRAS)
        self.color = random.choice(PALETA_ROJOS)
        self.alfa = 0
        self.parpadeo = random.uniform(0, math.pi * 2)
        self.fuente = None
        self.retraso = 0
        self.escala_extra = random.uniform(0.85, 1.15)


def punto_corazon(t):
    """La formula parametrica del corazon que use de base."""
    x = 16 * (math.sin(t) ** 3)
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return x, -y


def a_pantalla(x, y):
    return x * ESCALA + ANCHO / 2, y * ESCALA + ALTO / 2


def crear_contorno(cantidad, distancia_minima=26):
    """Primero dibujo solo el borde/contorno del corazon."""
    particulas = []
    colocadas = []
    for i in range(cantidad):
        t = (i / cantidad) * 2 * math.pi
        bx, by = punto_corazon(t)
        sx, sy = a_pantalla(bx, by)
        if any(math.hypot(sx - px, sy - py) < distancia_minima for (px, py) in colocadas):
            continue
        colocadas.append((sx, sy))
        particulas.append(Particula(sx, sy, i, "contorno"))
    return particulas


def crear_relleno(cantidad, distancia_minima=40):
    """Despues relleno el interior con mas palabras, ya mas al azar."""
    particulas = []
    colocadas = []
    intentos = 0
    max_intentos = cantidad * 80
    while len(particulas) < cantidad and intentos < max_intentos:
        intentos += 1
        t = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.0, 0.86)
        bx, by = punto_corazon(t)
        px, py = bx * r, by * r
        sx, sy = a_pantalla(px, py)
        if any(math.hypot(sx - qx, sy - qy) < distancia_minima for (qx, qy) in colocadas):
            continue
        colocadas.append((sx, sy))
        particulas.append(Particula(sx, sy, random.randint(0, 260), "relleno"))
    return particulas


def dibujar_con_brillo(capa_brillo, capa_texto, fuente, palabra, color, x, y, alfa, escala_extra=1.0):
    """Dibujo la palabra dos veces mas grande y transparente (para el
    brillo alrededor) y luego la palabra normal encima."""
    if alfa <= 0:
        return
    if escala_extra != 1.0:
        fuente_escalada = pygame.font.Font(None, int(fuente.get_height() * escala_extra))
        texto_render = fuente_escalada.render(palabra, True, color)
    else:
        texto_render = fuente.render(palabra, True, color)
    texto_render.set_alpha(alfa)
    rect_texto = texto_render.get_rect(center=(x, y))

    if alfa > 10:
        brillo_grande = pygame.transform.smoothscale(
            texto_render,
            (int(texto_render.get_width() * 2.2), int(texto_render.get_height() * 2.2)),
        )
        brillo_grande.set_alpha(max(0, alfa // 7))
        capa_brillo.blit(brillo_grande, brillo_grande.get_rect(center=(x, y)))

        brillo_chico = pygame.transform.smoothscale(
            texto_render,
            (int(texto_render.get_width() * 1.5), int(texto_render.get_height() * 1.5)),
        )
        brillo_chico.set_alpha(max(0, alfa // 3))
        capa_brillo.blit(brillo_chico, brillo_chico.get_rect(center=(x, y)))

    capa_texto.blit(texto_render, rect_texto)


def main():
    pygame.init()

    if os.path.exists(ARCHIVO_MUSICA):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(ARCHIVO_MUSICA)
            pygame.mixer.music.play()
        except Exception:
            pass  # si truena la musica, sigo sin musica, no pasa nada

    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.DOUBLEBUF)
    pygame.display.set_caption("I love you <3")
    reloj = pygame.time.Clock()

    fuente_contorno = pygame.font.SysFont("arial", 18, bold=True)
    fuente_relleno = pygame.font.SysFont("arial", 15, bold=True)
    fuente_centro = pygame.font.SysFont("georgia", 46, bold=True)

    fondo = pygame.Surface((ANCHO, ALTO))
    fondo.fill(COLOR_FONDO)

    contorno = crear_contorno(cantidad=140)
    relleno = crear_relleno(cantidad=110)

    rango_contorno = max(p.orden for p in contorno) if contorno else 0
    cuadros_por_paso = 1.6
    inicio_relleno = int(rango_contorno * cuadros_por_paso) + 30

    for p in relleno:
        p.retraso = inicio_relleno + p.orden
    for p in contorno:
        p.retraso = int(p.orden * cuadros_por_paso)

    particulas = contorno + relleno
    for p in particulas:
        p.fuente = fuente_contorno if p.tipo == "contorno" else fuente_relleno

    capa_brillo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    capa_texto = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

    corriendo = True
    cuadro = 0
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE
            ):
                corriendo = False

        pantalla.blit(fondo, (0, 0))
        capa_brillo.fill((0, 0, 0, 0))
        capa_texto.fill((0, 0, 0, 0))
        cuadro += 1

        for p in particulas:
            if cuadro > p.retraso and p.alfa < 255:
                p.alfa = min(255, p.alfa + 14 + random.randint(0, 4))

            if p.alfa >= 255:
                parpadeo = 0.75 + 0.25 * math.sin(cuadro * 0.04 + p.parpadeo)
            else:
                parpadeo = 1.0

            alfa_final = int(p.alfa * parpadeo)
            if alfa_final <= 0:
                continue

            dibujar_con_brillo(
                capa_brillo, capa_texto, p.fuente, p.palabra, p.color,
                p.x, p.y, alfa_final, p.escala_extra,
            )

        pantalla.blit(capa_brillo, (0, 0))
        pantalla.blit(capa_texto, (0, 0))

        # ya que se lleno el corazon, espero un poco y pongo el texto central
        inicio_centro = inicio_relleno + 200
        if cuadro > inicio_centro:
            progreso = min(1.0, (cuadro - inicio_centro) / 60)
            alfa_centro = int(255 * (1 - math.exp(-progreso * 8)))
            pulso = 1.0 + 0.025 * math.sin(cuadro * 0.05)

            superficie_centro = fuente_centro.render(TEXTO_CENTRAL, True, (255, 235, 230))
            ancho_nuevo = int(superficie_centro.get_width() * pulso)
            alto_nuevo = int(superficie_centro.get_height() * pulso)
            if ancho_nuevo > 0 and alto_nuevo > 0:
                superficie_centro = pygame.transform.smoothscale(
                    superficie_centro, (ancho_nuevo, alto_nuevo)
                )
            superficie_centro.set_alpha(alfa_centro)

            if alfa_centro > 10:
                brillo_centro = pygame.transform.smoothscale(
                    superficie_centro,
                    (int(superficie_centro.get_width() * 1.4), int(superficie_centro.get_height() * 1.4)),
                )
                brillo_centro.set_alpha(alfa_centro // 5)
                pantalla.blit(brillo_centro, brillo_centro.get_rect(center=(ANCHO / 2, ALTO / 2)))

            rect_centro = superficie_centro.get_rect(center=(ANCHO / 2, ALTO / 2))
            pantalla.blit(superficie_centro, rect_centro)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("OCURRIO UN ERROR:", e)
        import traceback
        traceback.print_exc()
