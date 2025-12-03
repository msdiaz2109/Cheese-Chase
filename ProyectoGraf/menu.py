import pygame
from OpenGL import GL as gl
import glm
from graficos_2d import ShaderUI
from clases_renderizado import ElementoInterfaz

class Menu:
    def __init__(self, resolucion):
        self.resolucion = resolucion
        self.shader = ShaderUI()
        self.quad = ElementoInterfaz.crear_quad_interfaz()
        self.fuente = pygame.font.SysFont("Arial", 48)
        self.opciones = [
            {"texto": "Principiante", "archivo": "Principiante.png", "nivel": 1},
            {"texto": "Intermedio", "archivo": "Intermedio.png", "nivel": 2},
            {"texto": "Avanzado", "archivo": "Avanzado.png", "nivel": 3},
            {"texto": "Salir", "archivo": "Salir.png", "nivel": 4}
        ]
        self.texturas_opciones = {}
        self._cargar_recursos()
        
        # Cargar fondo
        try:
            import os
            ruta_base = os.path.dirname(__file__)
            ruta_fondo = os.path.join(ruta_base, "recursos", "Menu", "menu.png")
            imagen_fondo = pygame.image.load(ruta_fondo)
            self.textura_fondo, _, _ = self._convertir_superficie(imagen_fondo)
        except Exception as error:
            print(f"No se pudo cargar el fondo: {error}")
            self.textura_fondo = None

    def _cargar_recursos(self):
        """Carga las texturas para las opciones del menú"""
        import os
        ruta_base = os.path.dirname(__file__)
        ruta_menu = os.path.join(ruta_base, "recursos", "Menu")
        
        for opcion in self.opciones:
            ruta_imagen = os.path.join(ruta_menu, opcion["archivo"])
            try:
                superficie_imagen = pygame.image.load(ruta_imagen).convert_alpha()
                self.texturas_opciones[opcion["texto"]] = self._convertir_superficie(superficie_imagen)
            except Exception as error:
                print(f"Error cargando {ruta_imagen}: {error}")
                # Usar texto como respaldo si falla la imagen
                superficie_texto = self.fuente.render(opcion["texto"], True, (255, 255, 255))
                self.texturas_opciones[opcion["texto"]] = self._convertir_superficie(superficie_texto)

    def _convertir_superficie(self, superficie):
        """Convierte una superficie de Pygame a una textura OpenGL"""
        superficie = pygame.transform.flip(superficie, False, True)
        ancho, alto = superficie.get_size()
        datos_imagen = pygame.image.tostring(superficie, "RGBA", 1)
        
        id_textura = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, id_textura)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, ancho, alto, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, datos_imagen)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        return id_textura, ancho, alto

    def ejecutar(self):
        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return 4
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # Convertir a coordenadas normalizadas si es necesario, o chequear colisión simple
                    # Verificar si se seleccionó alguna opción
                    seleccion = self._detectar_click(x, y)
                    if seleccion:
                        return seleccion

            self._renderizar()
            pygame.display.flip()
            reloj.tick(60)

    def _detectar_click(self, mouse_x, mouse_y):
        """Detecta si se hizo clic en alguna opción"""
        # Posición inicial y separación vertical
        inicio_y = 0.2
        separacion = 0.2
        
        # Convertir coordenadas del mouse a espacio normalizado (-1 a 1)
        x_normalizada = (mouse_x / self.resolucion[0]) * 2 - 1
        y_normalizada = -((mouse_y / self.resolucion[1]) * 2 - 1) # Invertir Y

        for i, opcion in enumerate(self.opciones):
            posicion_y = inicio_y - i * separacion
            # Dimensiones aproximadas del área de clic
            ancho_boton = 1.2
            alto_boton = 0.35
            
            # Verificar si el clic está dentro del botón
            if -ancho_boton/2 < x_normalizada < ancho_boton/2 and posicion_y - alto_boton/2 < y_normalizada < posicion_y + alto_boton/2:
                return opcion["nivel"]
        return None

    def _renderizar(self):
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        self.shader.activar()
        gl.glBindVertexArray(self.quad.id_contenedor)
        gl.glEnableVertexAttribArray(0)
        gl.glEnableVertexAttribArray(1)

        # Renderizar fondo
        if self.textura_fondo:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.textura_fondo)
            
            # Escalar para cubrir toda la pantalla (-1 a 1)
            # El quad es 0 a 1.
            # Trasladar a -1, -1 y escalar por 2.
            matriz = glm.mat4(1.0)
            matriz = glm.translate(matriz, glm.vec3(-1.0, -1.0, 0.0))
            matriz = glm.scale(matriz, glm.vec3(2.0, 2.0, 1.0))
            
            self.shader.set_transformacion(matriz)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.quad.num_vertices)

        inicio_y = 0.2
        separacion = 0.2

        for i, opcion in enumerate(self.opciones):
            id_textura, ancho, alto = self.texturas_opciones[opcion["texto"]]
            
            # Calcular escala para mantener la proporción de la imagen
            relacion_aspecto = ancho / alto
            escala_y = 0.35
            escala_x = escala_y * relacion_aspecto * (self.resolucion[1] / self.resolucion[0])

            posicion_y = inicio_y - i * separacion
            
            matriz = glm.mat4(1.0)
            # Centrar la imagen
            matriz = glm.translate(matriz, glm.vec3(-escala_x / 2.0, posicion_y - escala_y / 2.0, 0.0))
            matriz = glm.scale(matriz, glm.vec3(escala_x, escala_y, 1.0))
            
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, id_textura)
            self.shader.set_transformacion(matriz)
            
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.quad.num_vertices)

        gl.glDisableVertexAttribArray(0)
        gl.glDisableVertexAttribArray(1)
        gl.glBindVertexArray(0)
        self.shader.desactivar()
        gl.glDisable(gl.GL_BLEND)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def limpiar(self):
        self.shader.liberar_recursos()
        self.quad.limpiar()
        for id_textura, _, _ in self.texturas_opciones.values():
            gl.glDeleteTextures(1, [id_textura])
        if self.textura_fondo:
            gl.glDeleteTextures(1, [self.textura_fondo])
