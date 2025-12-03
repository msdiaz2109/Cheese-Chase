import glm
import random
from clases_renderizado import Modelo3D

class FractalNube:
    """Genera una nube fractal usando cubos recursivos"""
    def __init__(self, profundidad=3):
        self.profundidad = profundidad
        self.vertices = []
        self.normales = []
        self.colores = []
        self.coordenadas_textura = []
        
        # Generar el fractal desde el centro
        centro = glm.vec3(0.0, 0.0, 0.0)
        tamano = 1.0
        self._agregar_cubo_recursivo(centro, tamano, profundidad)

    def _agregar_cubo_recursivo(self, centro, tamano, profundidad):
        """Genera cubos de forma recursiva para crear el efecto fractal"""
        if profundidad == 0:
            return

        # Color aleatorio en tonos blancos/azulados para simular nube
        nivel_gris = random.uniform(0.85, 1.0)
        nivel_azul = random.uniform(0.9, 1.0)
        color = glm.vec3(nivel_gris, nivel_gris, nivel_azul)
        
        self._agregar_cubo(centro, tamano, color)
        
        # Direcciones para las 6 caras del cubo (+X, -X, +Y, -Y, +Z, -Z)
        direcciones = [
            glm.vec3(1, 0, 0), glm.vec3(-1, 0, 0),
            glm.vec3(0, 1, 0), glm.vec3(0, -1, 0),
            glm.vec3(0, 0, 1), glm.vec3(0, 0, -1)
        ]
        
        for direccion in direcciones:
            # 60% de probabilidad de crecer en cada dirección
            if random.random() > 0.4:
                # Reducir el tamaño para el siguiente nivel
                factor_reduccion = random.uniform(0.6, 0.8)
                tamano_hijo = tamano * factor_reduccion
                
                # Calcular posición del cubo hijo
                desplazamiento = direccion * (tamano * 0.5 + tamano_hijo * 0.5)
                
                # Añadir variación aleatoria para romper la uniformidad
                variacion = glm.vec3(
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3)
                ) * tamano
                
                centro_hijo = centro + desplazamiento + variacion
                
                self._agregar_cubo_recursivo(centro_hijo, tamano_hijo, profundidad - 1)

    def _agregar_cubo(self, centro, tamano, color):
        """Añade un cubo a la geometría del fractal"""
        radio = tamano * 0.5
        
        # Definir los 8 vértices del cubo
        vertices = [
            centro + glm.vec3(-radio, radio, -radio),   # 0: atrás-arriba-izquierda
            centro + glm.vec3(radio, radio, -radio),    # 1: atrás-arriba-derecha
            centro + glm.vec3(-radio, -radio, -radio),  # 2: atrás-abajo-izquierda
            centro + glm.vec3(radio, -radio, -radio),   # 3: atrás-abajo-derecha
            centro + glm.vec3(-radio, radio, radio),    # 4: frente-arriba-izquierda
            centro + glm.vec3(radio, radio, radio),     # 5: frente-arriba-derecha
            centro + glm.vec3(-radio, -radio, radio),   # 6: frente-abajo-izquierda
            centro + glm.vec3(radio, -radio, radio)     # 7: frente-abajo-derecha
        ]
        
        # Crear las 6 caras del cubo usando 2 triángulos por cara
        self._agregar_cara(vertices[4], vertices[5], vertices[1], vertices[0], glm.vec3(0, 1, 0), color)   # Arriba
        self._agregar_cara(vertices[2], vertices[3], vertices[7], vertices[6], glm.vec3(0, -1, 0), color)  # Abajo
        self._agregar_cara(vertices[6], vertices[7], vertices[5], vertices[4], glm.vec3(0, 0, 1), color)   # Frente
        self._agregar_cara(vertices[3], vertices[2], vertices[0], vertices[1], glm.vec3(0, 0, -1), color)  # Atrás
        self._agregar_cara(vertices[2], vertices[6], vertices[4], vertices[0], glm.vec3(-1, 0, 0), color)  # Izquierda
        self._agregar_cara(vertices[7], vertices[3], vertices[1], vertices[5], glm.vec3(1, 0, 0), color)   # Derecha

    def _agregar_cara(self, p0, p1, p2, p3, normal, color):
        """Añade una cara (2 triángulos) usando 4 vértices"""
        self._agregar_triangulo(p0, p1, p2, normal, color)
        self._agregar_triangulo(p0, p2, p3, normal, color)

    def _agregar_triangulo(self, punto1, punto2, punto3, normal, color):
        """Añade un triángulo a la geometría"""
        for punto in [punto1, punto2, punto3]:
            self.vertices.extend([punto.x, punto.y, punto.z])
            self.normales.extend([normal.x, normal.y, normal.z])
            self.colores.extend([color.x, color.y, color.z])
            self.coordenadas_textura.extend([0.0, 0.0])

    def crear_modelo(self):
        """Crea y retorna el modelo 3D del fractal"""
        cantidad_vertices = len(self.vertices) // 3
        modelo = Modelo3D(cantidad_vertices)
        
        modelo.cargar_datos_posicion(self.vertices)
        modelo.cargar_datos_normal(self.normales)
        modelo.cargar_datos_uv(self.coordenadas_textura)
        modelo.cargar_datos_color(self.colores)
            
        return modelo
