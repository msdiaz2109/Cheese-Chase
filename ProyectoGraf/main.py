import glm
import pygame
import pygame.display
from mundo import Mundo
from menu import Menu
import recursos
import sistemas_renderizado
import sistemas_renderizado_3d
import sistema_interfaz
import sistema_control

RESOLUCION = 1024, 720
FPS = 60
NIVEL = 1

def bucle_juego(mundo):
    reloj = pygame.time.Clock()
    ultimo_tiempo = pygame.time.get_ticks()
    mundo.sonido.reproducir('inicio')
    mundo.sonido.iniciar_musica()
    while True:
        # Calcular tiempo delta (diferencia de tiempo entre cuadros)
        tiempo_actual = pygame.time.get_ticks()
        mundo.delta = min(max((tiempo_actual - ultimo_tiempo) / 1000.0, 0.00000001), 0.1)
        mundo.tiempo = tiempo_actual / 1000.0
        ultimo_tiempo = tiempo_actual
        # Obtener eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.locals.K_ESCAPE:
                return
        # Actualizar
        
        # --- Lógica de Pausa ---
        if mundo.estado == recursos.ESTADO_EJECUTANDO or mundo.estado == recursos.ESTADO_INTRO or mundo.estado == recursos.ESTADO_VICTORIA or mundo.estado == recursos.ESTADO_DERROTA:
            mundo.process(mundo.delta)
        elif mundo.estado == recursos.ESTADO_PAUSADO:
            # Solo procesar renderizado y UI en pausa
            # Nota: esper no tiene un método process_group fácil, así que llamamos a los sistemas manualmente
            # O simplemente usamos process() pero los sistemas lógicos deben chequear el estado.
            # En este diseño, los sistemas corren siempre. Vamos a filtrar en main.
            
            # Opción B: Ejecutar solo sistemas de renderizado
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado.SistemaInicioCuadro))
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado_3d.SistemaConfiguracionLuz))
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado_3d.SistemaTransformacion))
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado_3d.SistemaInicioRenderizado))
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado_3d.SistemaRenderizadoModelos))
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado_3d.SistemaFinRenderizado))
            mundo._process(mundo.delta, mundo.get_processor(sistema_interfaz.SistemaUI))
            mundo._process(mundo.delta, mundo.get_processor(sistemas_renderizado.SistemaFinCuadro))
            
            # Permitir cambio de cámara en pausa
            mundo._process(mundo.delta, mundo.get_processor(sistema_control.SistemaControl))

        reloj.tick(FPS)

def main():
    pygame.init()
    pygame.display.init()
    
    pygame.display.set_mode(RESOLUCION, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("CHEESE CHASE")
    
    # Inicializar fuente para el menú
    pygame.font.init()

    while True:
        # Mostrar menú
        pygame.mouse.set_visible(True)
        menu = Menu(RESOLUCION)
        nivel = menu.ejecutar()
        menu.limpiar()

        if nivel == 4: # Salir
            break
            
        # Ejecutar juego
        pygame.mouse.set_visible(False)
        mundo = Mundo(glm.vec2(RESOLUCION), nivel)
        bucle_juego(mundo)
        mundo.limpiar()

    pygame.quit()


if __name__ == '__main__':
    main()
