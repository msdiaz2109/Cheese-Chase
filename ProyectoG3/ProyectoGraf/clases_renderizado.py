import ctypes
from OpenGL import GL as gl
from graficos_3d import ShaderEstandar

class ContenedorVertices:
    # Clase base para manejar la memoria de los vertices en la tarjeta grafica
    def __init__(self, num_vertices):
        # Crear un lugar en la GPU para guardar los datos
        self.id_contenedor = gl.glGenVertexArrays(1)
        self.num_vertices = num_vertices
        self.buffers = []

    def limpiar(self):
        # Liberar la memoria de la GPU
        for buffer in self.buffers:
            gl.glDeleteBuffers(1, [buffer])
        gl.glDeleteVertexArrays(1, [self.id_contenedor])

    def _guardar_datos(self, atributo, datos, componentes, tipo_arreglo_gl, tipo_gl, tamano_tipo):
        # Envia los datos (posiciones, colores, etc) a la tarjeta grafica
        gl.glBindVertexArray(self.id_contenedor)
        buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        self.buffers.append(buffer)
        tipo_arreglo = (tipo_arreglo_gl * len(datos))
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            len(datos) * tamano_tipo,
            tipo_arreglo(*datos),
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            atributo,
            componentes,
            tipo_gl,
            False,
            0,
            None
        )
        gl.glEnableVertexAttribArray(atributo)
        gl.glBindVertexArray(0)

    def _guardar_datos_f(self, atributo, datos, componentes):
        # Para numeros con decimales (floats)
        self._guardar_datos(
            atributo,
            datos,
            componentes,
            gl.GLfloat,
            gl.GL_FLOAT,
            ctypes.sizeof(ctypes.c_float))

    def _guardar_datos_int(self, atributo, datos, componentes, tipo_arreglo_gl, tipo_gl, tamano_tipo):
        # Para numeros enteros (ints)
        gl.glBindVertexArray(self.id_contenedor)
        buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        self.buffers.append(buffer)
        tipo_arreglo = (tipo_arreglo_gl * len(datos))
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            len(datos) * tamano_tipo,
            tipo_arreglo(*datos),
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribIPointer(
            atributo,
            componentes,
            tipo_gl,
            0,
            None
        )
        gl.glEnableVertexAttribArray(atributo)
        gl.glBindVertexArray(0)

class Modelo3D(ContenedorVertices):
    # Clase para objetos 3D normales (personajes, suelo, etc)
    def __init__(self, num_vertices):
        ContenedorVertices.__init__(self, num_vertices)
        self.tiene_skinning = False

    def cargar_datos_posicion(self, datos):
        self._guardar_datos_f(ShaderEstandar.ATRIBUTO_POSICION, datos, 3)

    def cargar_datos_normal(self, datos):
        self._guardar_datos_f(ShaderEstandar.ATRIBUTO_NORMAL, datos, 3)

    def cargar_datos_uv(self, datos):
        self._guardar_datos_f(ShaderEstandar.ATRIBUTO_COORD_TEXTURA, datos, 2)

    def cargar_datos_color(self, datos):
        self._guardar_datos_f(ShaderEstandar.ATRIBUTO_COLOR, datos, 3)

    def cargar_datos_skinning(self, articulaciones, pesos):
        # Para animar personajes (huesos y su influencia)
        self._guardar_datos_int(
            ShaderEstandar.ATRIBUTO_ARTICULACIONES, 
            articulaciones, 
            4, 
            gl.GLint, 
            gl.GL_INT, 
            ctypes.sizeof(ctypes.c_int)
        )
        self._guardar_datos_f(
            ShaderEstandar.ATRIBUTO_PESOS, 
            pesos, 
            4
        )
        self.tiene_skinning = True

    @staticmethod
    def crear_cubo(escala_uv=1.0):
        # Crea un cubo simple para pruebas o relleno
        puntos = [
            [-0.5, 0.5, -0.5],
            [0.5, 0.5, -0.5],
            [-0.5, -0.5, -0.5],
            [0.5, -0.5, -0.5],
            [-0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5],
            [-0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5]
        ]
        normales_lado = [
            [0.0, 0.0, -1.0],  # Abajo
            [0.0, 0.0, 1.0],  # Arriba
            [0.0, -1.0, 0.0],  # Frente
            [0.0, 1.0, 0.0],  # Atrás
            [-1.0, 0.0, 0.0],  # Izquierda
            [1.0, 0.0, 0.0]  # Derecha
        ]
        lados = [
            [2, 0, 1, 2, 1, 3],  # Abajo
            [4, 6, 5, 5, 6, 7],  # Arriba
            [2, 3, 7, 6, 2, 7],  # Frente
            [4, 5, 0, 0, 5, 1],  # Atrás
            [6, 4, 0, 0, 2, 6],  # Izquierda
            [5, 7, 3, 5, 3, 1]   # Derecha
        ]
        vertices = []
        normales = []
        coordenadas_textura = []
        
        coordenadas_textura_cara = [
            0.0, 0.0,
            1.0 * escala_uv, 0.0,
            1.0 * escala_uv, 1.0 * escala_uv,
            0.0, 0.0,
            1.0 * escala_uv, 1.0 * escala_uv,
            0.0, 1.0 * escala_uv
        ]
        for num_lado in range(6):
            for num_punto in range(6):
                punto = puntos[lados[num_lado][num_punto]]
                vertices.append(punto[0])
                vertices.append(punto[1])
                vertices.append(punto[2])
                normal = normales_lado[num_lado]
                normales.append(normal[0])
                normales.append(normal[1])
                normales.append(normal[2])
                
                coordenadas_textura.append(coordenadas_textura_cara[num_punto * 2])
                coordenadas_textura.append(coordenadas_textura_cara[num_punto * 2 + 1])
        
        modelo = Modelo3D(6 * 6)
        modelo.cargar_datos_posicion(vertices)
        modelo.cargar_datos_normal(normales)
        modelo.cargar_datos_uv(coordenadas_textura)
        modelo.cargar_datos_color([1.0] * (6 * 6 * 3))
        return modelo

class ElementoInterfaz(ContenedorVertices):
    # Clase para cosas 2D de la interfaz (vidas, menu)
    def __init__(self, num_vertices):
        ContenedorVertices.__init__(self, num_vertices)

    def cargar_datos_posicion(self, datos):
        self._guardar_datos_f(0, datos, 2)

    def cargar_datos_uv(self, datos):
        self._guardar_datos_f(1, datos, 2)

    @staticmethod
    def crear_quad_interfaz():
        # Crea un cuadrado plano para dibujar imagenes 2D
        vertices = [
            0.0, 1.0,
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0
        ]
        indices = [0, 1, 2, 0, 2, 3]
        
        lista_vertices = []
        for i in indices:
            lista_vertices.append(vertices[i*2])
            lista_vertices.append(vertices[i*2+1])
            
        coordenadas_textura = [
            0.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
            1.0, 0.0
        ]
        
        lista_coordenadas_textura = []
        for i in indices:
            lista_coordenadas_textura.append(coordenadas_textura[i*2])
            lista_coordenadas_textura.append(coordenadas_textura[i*2+1])

        interfaz = ElementoInterfaz(6)
        interfaz.cargar_datos_posicion(lista_vertices)
        interfaz.cargar_datos_uv(lista_coordenadas_textura)
        return interfaz
