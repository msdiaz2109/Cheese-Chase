"""
Implementación en Python de un algoritmo de generación de laberintos:
https://en.wikipedia.org/wiki/Maze_generation_algorithm
"""
import math
from random import randint
import componentes_3d as componentes
import glm
import recursos

def _crear_pared(posicion_x, posicion_y, mundo, ancho, alto, profundidad, id_modelo, color_difuso, id_textura, escala_uv, usar_world_uv=False):
    """Crea una entidad de pared en el mundo"""
    mundo.create_entity(
        componentes.Modelo3D(id_modelo),
        componentes.Transformacion(
            posicion=glm.vec3(posicion_x + ancho / 2, posicion_y + alto / 2, profundidad / 2),
            escala=glm.vec3(float(ancho), float(alto), profundidad)),
        componentes.CajaDelimitadora(componentes.Rectangulo3D(float(ancho), float(alto), profundidad)),
        componentes.MatrizTransformacion(),
        componentes.MaterialObjeto(difuso=color_difuso, id_textura=id_textura, escala_uv=escala_uv, usar_world_uv=usar_world_uv)
    )

def _configurar_laberinto(mundo, ancho, alto, profundidad=2.0, ancho_pared=1.0, ancho_camino=3.0):
    """Genera y configura el laberinto en el mundo del juego"""
    # Obtener IDs de modelos
    id_modelo_cubo = mundo.registro_modelos.obtener_id(recursos.GestorRecursos.CUBO)
    id_modelo_suelo = mundo.registro_modelos.obtener_id(recursos.GestorRecursos.SUELO)
    
    # Generar el laberinto
    laberinto = Laberinto(ancho=ancho, largo=alto)
    mapa = laberinto.generar()
    mapa[1][1] = False  # Asegurar espacio libre en el inicio
    
    # Calcular dimensiones del suelo
    dimensiones_suelo = glm.vec2(
        ancho * (ancho_pared + ancho_camino) / 2, 
    )
    laberinto.centro = glm.vec3(
        dimensiones_suelo.x / 2 + ancho_pared / 2, 
        dimensiones_suelo.y / 2 + ancho_pared / 2, 
        0
    )
    
    # Obtener texturas
    textura_suelo = mundo.registro_modelos.obtener_textura("pasto")
    textura_pared = mundo.registro_modelos.obtener_textura(recursos.GestorRecursos.ARBUSTO)
    
    # Crear el suelo del laberinto
    mundo.create_entity(
        componentes.Modelo3D(id_modelo_suelo),
        componentes.Transformacion(
            posicion=glm.vec3(laberinto.centro.x, laberinto.centro.y, -(ancho_camino / 2)),
            escala=glm.vec3(dimensiones_suelo.x, dimensiones_suelo.y, ancho_camino)),
        componentes.CajaDelimitadora(componentes.Rectangulo3D(dimensiones_suelo.x, dimensiones_suelo.y, ancho_camino)),
        componentes.MatrizTransformacion(),
        componentes.MaterialObjeto(
            difuso=glm.vec3(1.0, 1.0, 1.0),
            id_textura=textura_suelo,
            especular=glm.vec3(0.2, 0.3, 0.6),
            brillo=6)
    )
    
    # Generar las paredes del laberinto
    posicion_y = 0
    for fila in range(len(mapa[0])):
        posicion_x = 0
        altura_celda = ancho_pared if fila % 2 == 0 else ancho_camino
        
        # Variables para combinar paredes adyacentes
        ancho_pared_actual = 0
        inicio_pared = 0
        construyendo_pared = False
        
        for columna in range(len(mapa[0]) + 1):
            ancho_celda = ancho_pared if columna % 2 == 0 else ancho_camino
            
            # Verificar si esta celda es una pared
            es_pared = columna < len(mapa[0]) and mapa[fila][columna]
            
            if es_pared:
                if not construyendo_pared:
                    construyendo_pared = True
                    inicio_pared = posicion_x
                ancho_pared_actual += ancho_celda
            elif construyendo_pared:
                # Crear pared combinada
                color = glm.vec3(1.0, 1.0, 1.0)
                escala_textura = glm.vec3(0.5, 0.5, 0.5)
                
                _crear_pared(
                    inicio_pared, posicion_y, mundo, 
                    ancho_pared_actual, altura_celda, profundidad, 
                    id_modelo_cubo, color, textura_pared, escala_textura, 
                    usar_world_uv=True
                )
                
                construyendo_pared = False
                ancho_pared_actual = 0
            elif (fila % 2 == 0 or columna % 2 == 0):
                # Registrar áreas vacías para colocar objetos
                laberinto.areas_vacias.append([posicion_x + ancho_celda / 2, posicion_y + altura_celda / 2])
            
            posicion_x += ancho_celda
        posicion_y += altura_celda
    return laberinto

class Laberinto:
    """Genera laberintos usando el algoritmo de crecimiento recursivo"""
    
    def __init__(self, ancho=30, largo=30, complejidad=0.75, densidad=0.75):
        # Valores mínimos recomendados: ancho=6, largo=6
        self.ancho = ancho
        self.alto = largo
        self.complejidad = complejidad
        self.densidad = densidad
        self.dimensiones = ((self.alto // 2) * 2 + 1, (self.ancho // 2) * 2 + 1)
        self.mapa = []
        self.centro = glm.vec3()
        self.areas_vacias = []
    
    def generar(self):
        """Genera el mapa del laberinto usando el algoritmo de crecimiento recursivo"""
        # Calcular parámetros basados en complejidad y densidad
        nivel_complejidad = int(self.complejidad * (5 * (self.dimensiones[0] + self.dimensiones[1])))
        nivel_densidad = int(self.densidad * ((self.dimensiones[0] // 2) * (self.dimensiones[1] // 2)))
        
        # Inicializar mapa vacío
        mapa = [[False] * self.dimensiones[0] for _ in range(self.dimensiones[0])]
        
        # Crear bordes del laberinto
        mapa[0] = mapa[len(mapa) - 1] = [True] * self.dimensiones[0]
        for fila in range(1, len(mapa) - 1):
            mapa[fila][0] = mapa[fila][len(mapa) - 1] = True
        
        # Generar caminos del laberinto
        for _ in range(nivel_densidad):
            posicion_x = randint(0, self.dimensiones[0] // 2) * 2
            posicion_y = randint(0, self.dimensiones[1] // 2) * 2
            mapa[posicion_y][posicion_x] = True
            
            # Crecer desde este punto
            for _ in range(nivel_complejidad):
                # Encontrar celdas vecinas
                vecinos = []
                if posicion_x > 1:
                    vecinos.append((posicion_y, posicion_x - 2))
                if posicion_x < self.dimensiones[1] - 2:
                    vecinos.append((posicion_y, posicion_x + 2))
                if posicion_y > 1:
                    vecinos.append((posicion_y - 2, posicion_x))
                if posicion_y < self.dimensiones[0] - 2:
                    vecinos.append((posicion_y + 2, posicion_x))
                
                if vecinos:
                    # Seleccionar vecino aleatorio
                    vecino_y, vecino_x = vecinos[randint(0, len(vecinos) - 1)]
                    
                    if not mapa[vecino_y][vecino_x]:
                        # Marcar vecino y celda intermedia como pared
                        mapa[vecino_y][vecino_x] = True
                        mapa[vecino_y + (posicion_y - vecino_y) // 2][vecino_x + (posicion_x - vecino_x) // 2] = True
                        posicion_x, posicion_y = vecino_x, vecino_y
        
        self.mapa = mapa
        return mapa
