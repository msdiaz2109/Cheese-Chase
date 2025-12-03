
import numpy as np
import sys
import io
from utilidades_gltf import UtilidadesGltf
import pygame
from OpenGL import GL as gl

class CargadorGlb:
    # Clase para cargar archivos GLB (modelos 3D con texturas y animaciones)
    def __init__(self, archivo):
        self.archivo = archivo
        self.vertices = []
        self.normales = []
        self.coordenadas_textura = []
        self.colores = []
        self.articulaciones = []
        self.pesos = []
        
        # Datos de animacion de huesos
        self.matrices_huesos = None
        self.nodos_huesos = None
        self.datos_json = None
        self.imagenes = []
        self.materiales = []
        self.indice_textura = None

    def cargar(self):
        # Intentar cargar el archivo
        try:
            # Intentar ruta relativa primero
            ruta = sys.path[0] + "/" + self.archivo
            
            # Cargar todos los datos manualmente
            modelo_cargado = UtilidadesGltf.cargar_modelo(ruta)
            
            self.matrices_huesos = modelo_cargado['inverse_bind_matrices']
            self.nodos_huesos = modelo_cargado['joint_nodes']
            self.datos_json = modelo_cargado['json']
            self.imagenes = modelo_cargado.get('images', [])
            self.materiales = modelo_cargado.get('materials', [])
            
            # Procesar primitivas
            for primitiva in modelo_cargado['primitives']:
                # Obtener datos
                posiciones = primitiva['positions']
                normales = primitiva['normals']
                coordenadas_textura = primitiva['uvs']
                articulaciones = primitiva['joints']
                pesos = primitiva['weights']
                indices = primitiva['indices']
                
                # Color por defecto (blanco)
                r, g, b = 1.0, 1.0, 1.0
                
                # Verificar color del material
                indice_material = primitiva.get('material')
                if indice_material is not None and indice_material < len(self.materiales):
                    material = self.materiales[indice_material]
                    color_material = material['baseColor']
                    r, g, b = color_material[0], color_material[1], color_material[2]
                    
                    # Guardar índice de textura si existe
                    if 'baseColorTextureIndex' in material:
                        self.indice_textura = material['baseColorTextureIndex']
                
                # Desenrollar índices
                if indices is not None:
                    # Aplanar índices si son (N, 1)
                    indices = indices.flatten()
                    for i in indices:
                        # Posición
                        self.vertices.extend(posiciones[i])
                        # Normal
                        if normales is not None:
                            self.normales.extend(normales[i])
                        else:
                            self.normales.extend([0, 1, 0])
                        # UV
                        if coordenadas_textura is not None:
                            self.coordenadas_textura.extend(coordenadas_textura[i])
                        else:
                            self.coordenadas_textura.extend([0.0, 0.0])
                        # Color
                        self.colores.extend([r, g, b])
                        # Skinning
                        if articulaciones is not None and pesos is not None:
                            self.articulaciones.extend(articulaciones[i])
                            self.pesos.extend(pesos[i])
                else:
                    # No indexado, solo iterar posiciones
                    total = len(posiciones)
                    for i in range(total):
                        self.vertices.extend(posiciones[i])
                        if normales is not None:
                            self.normales.extend(normales[i])
                        else:
                            self.normales.extend([0, 1, 0])
                        if coordenadas_textura is not None:
                            self.coordenadas_textura.extend(coordenadas_textura[i])
                        else:
                            self.coordenadas_textura.extend([0.0, 0.0])
                        self.colores.extend([r, g, b])
                        if articulaciones is not None and pesos is not None:
                            self.articulaciones.extend(articulaciones[i])
                            self.pesos.extend(pesos[i])



        except Exception as e:
            print(f"Fallo al cargar GLB {self.archivo}: {e}")
            raise e

        return self._crear_modelo()

    def _crear_modelo(self):
        from clases_renderizado import Modelo3D
        # Crea el modelo 3D con los datos cargados
        num_vertices = len(self.vertices) // 3
        modelo = Modelo3D(num_vertices)
        
        modelo.cargar_datos_posicion(self.vertices)
        modelo.cargar_datos_normal(self.normales)
        
        if self.coordenadas_textura:
            modelo.cargar_datos_uv(self.coordenadas_textura)
            
        if self.colores:
             modelo.cargar_datos_color(self.colores)
        else:
             # Blanco por defecto
             modelo.cargar_datos_color([1.0] * (num_vertices * 3))
             
        if self.articulaciones and self.pesos:
            modelo.cargar_datos_skinning(self.articulaciones, self.pesos)
            
        return modelo

    def extraer_textura(self, flip_y=False):
        # Extrae la textura del archivo GLB y la sube a OpenGL
        if not self.imagenes:
            return None
        
        num_imagen = 0
        if self.indice_textura is not None and self.indice_textura < len(self.imagenes):
            num_imagen = self.indice_textura

        try:
            datos_imagen = self.imagenes[num_imagen]
            if datos_imagen is None:
                return None
            
            bytes_imagen = datos_imagen['data']
            
            # Cargar imagen con Pygame
            stream = io.BytesIO(bytes_imagen)
            imagen = pygame.image.load(stream)
            
            if flip_y:
                imagen = pygame.transform.flip(imagen, False, True)
                
            ancho, alto = imagen.get_size()
            bytes_textura = pygame.image.tostring(imagen, "RGB", False)
            
            # Generar textura OpenGL
            textura_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, textura_id)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, ancho, alto, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, bytes_textura)
            
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            

            return textura_id

        except Exception as e:
            print(f"Fallo al extraer textura de GLB {self.archivo}: {e}")
            return None

    def extraer_color(self):
        # Extrae el color del primer material
        if self.materiales:
            color = self.materiales[0]['baseColor']
            return (color[0], color[1], color[2])
        return None

    def extraer_esqueleto(self):
        # Extrae los datos de los huesos para animacion
        if self.matrices_huesos is not None:
            return {
                'inverse_bind_matrices': self.matrices_huesos,
                'joint_nodes': self.nodos_huesos,
                'json': self.datos_json
            }
        return None
