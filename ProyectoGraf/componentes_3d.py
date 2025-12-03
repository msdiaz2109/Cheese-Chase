import math
import glm
#
# Física de objetos
#
class Velocidad:
    def __init__(self, x=0.0, y=0.0, z=0.0, a_lo_largo_eje_mundo=True, permitir_pausa=False):
        self.valor = glm.vec3(x, y, z)
        self.a_lo_largo_eje_mundo = a_lo_largo_eje_mundo
        self.permitir_pausa = permitir_pausa
class Gato:
    pass
class Victoria:
    def __init__(self):
        self.juego_terminado = False
        self.tiempo_animacion = 0
        self.ganado = False
class ComponenteColision:
    def __init__(self):
        self.esta_colisionando_y = False
        self.esta_colisionando_x = False
        self.esta_colisionando_z = False
class ReporteColision:
    def __init__(self):
        self.fallido = []
class ObjetoFisico:
    def __init__(self):
        self.tiempo_aire = 0.0
class AnimacionLuz:
    def __init__(self, color_base, color_agregar, factor_delta=1.0):
        self.color_base = color_base
        self.color_agregar = color_agregar
        self.factor_delta = factor_delta
        self.delta_animacion = 0.0
        self.habilitado = True
#
# Componentes de control
#
class Casa:
    def __init__(self, posicion=glm.vec3(), rotacion=glm.vec3()):
        self.posicion = posicion * 1.0
        self.rotacion = rotacion * 1.0
#
# Traslación de Objeto
#
class Transformacion:
    def __init__(self,
            posicion=glm.vec3(),
            escala=glm.vec3(1.0, 1.0, 1.0),
            rotacion=glm.vec3()):
        self.posicion = posicion * 1.0
        self.escala = escala * 1.0
        self.rotacion = rotacion * 1.0
class MatrizTransformacion:
    def __init__(self):
        self.valor = glm.mat4x4(1.0)
#
# Cámara
#
class OrientacionCamara:
    def __init__(self):
        self.mirar_a = glm.vec3(0.0, 1.0, 0.0)
        self.arriba = glm.vec3(0.0, 0.0, 1.0)
class CamaraLibre:
    pass
class CamaraTerceraPersona:
    def __init__(self, objetivo, distancia=1.0, inclinacion=0.0, guiñada=0.0):
        self.objetivo = objetivo
        self.distancia = distancia
        self.inclinacion = inclinacion
        self.guiñada = guiñada
#
# Forma
#
class CajaDelimitadora:
    def __init__(self, forma):
        self.forma = forma
        self.radio = forma.obtener_radio()
class Rectangulo3D:
    """
    Esto no debe ser rotado ni escalado. Vista superior:
    
    ancho (eje x)
    #######
    #  1  # profundidad (eje y)
    #######
    
    1 es la altura (eje z)
    """
    def __init__(self, ancho, profundidad, altura):
        self.ancho = ancho / 2.0
        self.profundidad = profundidad / 2.0
        self.altura = altura / 2.0
    def min_x(self):
        return -self.ancho
    def max_x(self):
        return self.ancho
    def min_y(self):
        return -self.profundidad
    def max_y(self):
        return self.profundidad
    def min_z(self):
        return -self.altura
    def max_z(self):
        return self.altura
    def obtener_radio(self):
        return math.sqrt(self.ancho ** 2 + self.profundidad ** 2 + self.altura ** 2)

class Circulo:
    def __init__(self, centro_x, centro_y, radio):
        self.posicion = glm.vec2(centro_x, centro_y)
        self.radio = radio
#
# Gráficos
#
class Modelo3D:
    def __init__(self, id_modelo):
        self.id_modelo = id_modelo
class MaterialObjeto:
    def __init__(self,
                 difuso=glm.vec3(0, 0, 0),
                 especular=glm.vec3(0, 0, 0),
                 brillo=5,
                 id_textura=None,
                 escala_uv=glm.vec3(1.0, 1.0, 1.0),
                 usar_world_uv=False):
        self.difuso = difuso * 1.0
        self.especular = especular * 1.0
        self.brillo = brillo
        self.id_textura = id_textura
        self.escala_uv = escala_uv
        self.usar_world_uv = usar_world_uv
class Luz:
    def __init__(
            self,
            color=glm.vec3(),
            atenuacion=glm.vec3(0.0, 0.0, 1.0),
            habilitado=True):
        self.color = color * 1.0
        self.atenuacion = atenuacion * 1.0
        self.habilitado = habilitado
        # La atenuación se calcula como: 
        #   d := distancia
        #   atenuacion.x * d^2 + atenuacion.y * d + atenuacion.z

class Esqueleto:
    def __init__(self, datos_esqueleto):
        self.matrices_vinculacion_inversa = datos_esqueleto['inverse_bind_matrices']
        self.nodos_articulacion = datos_esqueleto['joint_nodes']
        self.datos_json = datos_esqueleto['json']
        
        self.conteo_articulaciones = len(self.nodos_articulacion)
        self.matrices_articulacion = [glm.mat4(1.0)] * self.conteo_articulaciones
        
        # Para animación procedural: mapa indice_nodo -> rotación local (quat o euler)
        # Usaremos euler por simplicidad por ahora, o quat si es necesario.
        self.rotaciones_hueso = {} 
