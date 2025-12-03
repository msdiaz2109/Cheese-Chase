import math
import random
import esper
import glm
import pygame
from sonido import Sonido
import componentes_3d as componentes
import sistema_control as sistemas_control
import sistemas_fisicos as sistemas_fisicos
import sistemas_renderizado as sistemas_renderizado
import sistemas_renderizado_3d as sistemas_renderizado_3d
import recursos
from laberinto import _configurar_laberinto
from graficos_3d import ShaderEstandar
from clases_renderizado import Modelo3D
import sistema_animacion as sistema_animacion
from sistema_interfaz import SistemaUI
from curvas_bezier import CurvaBezier
from curvas_bspline import CurvaBSpline
import modelos_color

class Mundo(esper.World):
    def __init__(self, resolucion, nivel):
        super().__init__()
        self.sonido = Sonido()
        self.resolucion = resolucion
        self.estado = recursos.ESTADO_INTRO
        self.vida = 3
        self.nivel = nivel
        self.shader_estandar = ShaderEstandar()
        self.delta = 0.00001
        self.tiempo = 0.0
        self.tiempo_intro = 0.0
        self.duracion_intro = 4.0 # Segundos
        
        # Puntos de control para la intro (Curva de Bézier)
        # Inicio (Arriba y lejos, centrado en X)
        self.punto_inicio = glm.vec3(15.0, -30.0, 60.0)
        # Primer punto de control: Bajando hacia el laberinto
        self.punto_control_1 = glm.vec3(15.0, 0.0, 45.0)
        # Segundo punto de control: Acercándose al jugador (desde arriba)
        self.punto_control_2 = glm.vec3(2.0, 2.0, 25.0)
        # El punto final se calculará dinámicamente basado en la posición inicial de la cámara del jugador
        # P3 se calculará dinámicamente basado en la posición inicial de la cámara del jugador
        
        self.curva_intro = None # Se inicializa en _configurar_entidades
        
        # Variables para la victoria
        self.curva_victoria = None
        self.tiempo_victoria = 0.0
        self.duracion_vuelta_victoria = 30.0 # Segundos por vuelta (Aún más lento)

        self.configuracion_luz = recursos.ConfiguracionIluminacion(ambiente_global=glm.vec3(0.6, 0.6, 0.6))
        self.controles = recursos.ControlJuego()
        self.registro_modelos = recursos.GestorRecursos()
        self.id_camara = 0
        self.matriz_vista = glm.mat4(1.0)
        self.ancho_laberinto = 30
        self.largo_laberinto = 30
        self.laberinto = _configurar_laberinto(self, self.ancho_laberinto, self.largo_laberinto, profundidad=1.5)
        self._inicializar_sistemas()
        self._crear_entidades_base()
        self._crear_nivel()
        self.actualizar_resolucion(resolucion)

    def process(self, dt=0):
        # Procesar intro
        if self.estado == recursos.ESTADO_INTRO:
            self.tiempo_intro += self.delta
            t = min(self.tiempo_intro / self.duracion_intro, 1.0)
            
            # Actualizar posición de cámara libre
            if self.curva_intro:
                # Calcular nueva posición en la curva
                nueva_pos = self.curva_intro.calcular_punto(t)
                transformacion_camara = self.component_for_entity(self.cam_libre, componentes.Transformacion)
                transformacion_camara.posicion = nueva_pos
                
                # Mirar siempre al centro o interpolar hacia donde mira el jugador
                centro = glm.vec3(15, 15, 0)
                jugador_pos = glm.vec3(2.0, 2.0, 1.0) # Posición conocida del jugador
                
                # Interpolación lineal del objetivo de la cámara
                # Al principio mira al centro, al final mira al jugador
                mirar_a = centro * (1.0 - t) + jugador_pos * t
                
                self.component_for_entity(self.cam_libre, componentes.OrientacionCamara).mirar_a = mirar_a

            if t >= 1.0:
                self.estado = recursos.ESTADO_EJECUTANDO
                self.id_camara = self.cam_jugador
                self.controles.modo_control = recursos.ControlJuego.MODO_JUGADOR
        
        # Procesar Victoria o Derrota (Cámara B-Spline + Luces HSV)
        elif self.estado == recursos.ESTADO_VICTORIA or self.estado == recursos.ESTADO_DERROTA:
            self.tiempo_victoria += self.delta
            
            # 1. Movimiento de Cámara (B-Spline)
            if self.curva_victoria:
                # t cíclico de 0.0 a 1.0
                t = (self.tiempo_victoria % self.duracion_vuelta_victoria) / self.duracion_vuelta_victoria
                
                nueva_pos = self.curva_victoria.calcular_punto(t)
                transformacion_camara = self.component_for_entity(self.cam_libre, componentes.Transformacion)
                transformacion_camara.posicion = nueva_pos
                
                # Mirar siempre al centro del laberinto
                centro = glm.vec3(self.laberinto.centro.x, self.laberinto.centro.y, 0)
                self.component_for_entity(self.cam_libre, componentes.OrientacionCamara).mirar_a = centro

            # 2. Luces de Fiesta (Modelo HSV)
            # Variar el matiz (Hue) con el tiempo
            hue = (self.tiempo_victoria * 30.0) % 360.0 # Más lento: 30 grados por segundo
            
            # Usar menor saturación (0.4) para colores pastel y buen brillo (0.8)
            # Esto evita que se vea "quemado" o muy oscuro
            color_fiesta = modelos_color.hsv_a_rgb(hue, 0.4, 0.8) 
            
            # Aplicar a la luz ambiental global
            self.configuracion_luz.ambiente_global = color_fiesta
            
            # Opcional: Aplicar a la luz central
            # (Asumiendo que la luz central es la primera entidad con componente Luz creada en _crear_nivel)
            # Pero modificar el ambiente global es más efectivo para "llenar" la escena de color.


        super().process()

    def limpiar(self):
        # Limpiar recursos de OpenGL explícitamente
        # Es necesario hacerlo antes de que PyOpenGL se destruya al salir
        for _entidad, vbo in self.get_component(Modelo3D):
            vbo.limpiar()
        self.registro_modelos.limpiar()
        self.shader_estandar.liberar_recursos()
        for processor in self._processors:
            if hasattr(processor, 'limpiar'):
                processor.limpiar()


    def _inicializar_sistemas(self):
        """Inicializa y agrega todos los sistemas del juego al mundo"""
        # Física
        sistemas_control.agregar_sistemas_control(self)
        sistemas_fisicos.agregar_sistemas(self)
        
        # Animación
        self.add_processor(sistema_animacion.SistemaAnimacion())

        # Renderizado
        sistemas_control.agregar_sistemas_camara(self)
        self.add_processor(sistemas_renderizado.SistemaInicioCuadro())
        sistemas_renderizado_3d.agregar_sistemas(self)
        self.add_processor(SistemaUI())
        self.add_processor(sistemas_renderizado.SistemaFinCuadro())

    def _crear_entidades_base(self):
        """Crea las entidades básicas como el jugador y las cámaras"""
        # Configurar entidad del jugador (Ratón)
        
        # Obtener textura del registro (cargada desde GLB)
        id_textura_raton = self.registro_modelos.obtener_textura(recursos.GestorRecursos.RATON)
        color_raton = self.registro_modelos.obtener_color(recursos.GestorRecursos.RATON)
        
        color_difuso = glm.vec3(1.0, 1.0, 1.0)
        if color_raton:
             color_difuso = glm.vec3(color_raton[0], color_raton[1], color_raton[2])
        posicion = glm.vec3(2.0, 2.0, 1.0)
        
        rotacion = glm.vec3(1.57, 0.0, 0.0)
        
        self.objeto_jugador = self.create_entity(
            componentes.Modelo3D(self.registro_modelos.obtener_id(recursos.GestorRecursos.RATON)),
            componentes.Transformacion(posicion=posicion, rotacion=rotacion, escala=glm.vec3(0.7, 0.7, 0.7)),
            componentes.MatrizTransformacion(),
            componentes.MaterialObjeto(difuso=color_difuso, id_textura=id_textura_raton),
            componentes.Velocidad(a_lo_largo_eje_mundo=True),
            componentes.Casa(posicion, rotacion),
            componentes.CajaDelimitadora(componentes.Rectangulo3D(0.7, 0.7, 0.7)),
            componentes.ComponenteColision(),
            componentes.ObjetoFisico(),
            componentes.Luz(atenuacion=glm.vec3(0.1, 0.0, 1.0)),
            componentes.AnimacionLuz(color_base=glm.vec3(1.0, 0.0, 0.5), color_agregar=glm.vec3(0.1, 0.1, 0.1), factor_delta=0.5)
        )
        
        # Agregar Esqueleto si está disponible
        datos_esqueleto = self.registro_modelos.obtener_esqueleto(recursos.GestorRecursos.RATON)
        if datos_esqueleto:
            self.add_component(self.objeto_jugador, componentes.Esqueleto(datos_esqueleto))


        self.cam_jugador = self.create_entity(
            componentes.CamaraTerceraPersona(self.objeto_jugador, distancia=3.0, inclinacion=-0.5),
            componentes.OrientacionCamara(),
            componentes.Transformacion()
        )
        
        # Objeto nariz de depuración (Invisible pero funcional)
        self.objeto_nariz = self.create_entity(
            componentes.Transformacion(escala=glm.vec3(0.1, 0.1, 0.1)), 
            componentes.MatrizTransformacion(),
            componentes.Casa()
        )
        posicion = glm.vec3(-5.0, -5.0, 20.0)
        rotacion = glm.vec3(-0.5, 0.0, 0.9)
        self.cam_libre = self.create_entity(
            componentes.Transformacion(posicion=posicion, rotacion=rotacion),
            componentes.Velocidad(a_lo_largo_eje_mundo=True, permitir_pausa=True),
            componentes.CamaraLibre(),
            componentes.OrientacionCamara(),
            componentes.Casa(posicion, rotacion))



        self.id_camara = self.cam_jugador
        
        # Configurar curva de intro
        # Punto final: Posición final estimada de la cámara (detrás del jugador)
        # El jugador está en (2, 2, 1). La cámara suele estar atrás y arriba.
        punto_final = glm.vec3(2.0, -1.0, 3.0) 
        
        self.curva_intro = CurvaBezier(self.punto_inicio, self.punto_control_1, self.punto_control_2, punto_final)
        
        # Cámara inicial es la libre para la intro
        self.id_camara = self.cam_libre
        transformacion_camara_libre = self.component_for_entity(self.cam_libre, componentes.Transformacion)
        transformacion_camara_libre.posicion = self.punto_inicio
        # Orientar hacia el centro aprox
        self.component_for_entity(self.cam_libre, componentes.OrientacionCamara).mirar_a = glm.vec3(15, 15, 0)

    def _crear_nivel(self):
        """Crea los objetos del nivel: luces, enemigos (gatos), objetivo (queso) y decoración"""
        # Luz central
        self.create_entity(
            componentes.Transformacion(posicion=glm.vec3(self.laberinto.centro.x, self.laberinto.centro.y, 20.0)),
            componentes.Luz(color=glm.vec3(0.5, 0.4, 0.4))
        )

        # Configuración de gatos
        max_luces_gatos = self.configuracion_luz.MAX_CONTEO_LUZ - 2 - 1
        valor_min = min(self.ancho_laberinto, self.largo_laberinto)
        cantidad_gatos = self.nivel * valor_min * 0.2
        
        # Mínimo de gatos
        if cantidad_gatos < 5:
            cantidad_gatos = 5
        
        # Obtener textura del registro (cargada desde GLB)
        id_textura_gato = self.registro_modelos.obtener_textura(recursos.GestorRecursos.GATO)
        color_gato = self.registro_modelos.obtener_color(recursos.GestorRecursos.GATO)
        
        # Color por defecto si no se encuentra nada (blanco)
        color_difuso = glm.vec3(1.0, 1.0, 1.0)
        if color_gato:
             color_difuso = glm.vec3(color_gato[0], color_gato[1], color_gato[2])

        # Asegurar ubicaciones de aparición únicas
        lugares_disponibles = len(self.laberinto.areas_vacias)
        cantidad_final = int(cantidad_gatos)
        if cantidad_final > lugares_disponibles:
            cantidad_final = lugares_disponibles
            
        indices_elegidos = random.sample(range(lugares_disponibles), cantidad_final)

        for i, idx in enumerate(indices_elegidos):
            x, y = self.laberinto.areas_vacias[idx]
            posicion = glm.vec3(x, y, 3.0)
            self.gato = self.create_entity(
                componentes.Modelo3D(self.registro_modelos.obtener_id(recursos.GestorRecursos.GATO)),
                componentes.Gato(),
                componentes.Transformacion(posicion=posicion, rotacion=glm.vec3(1.57, 0.0, 0.0), escala=glm.vec3(0.12, 0.12, 0.12)),
                componentes.MatrizTransformacion(),
                componentes.MaterialObjeto(difuso=glm.vec3(1.0, 1.0, 1.0), id_textura=id_textura_gato),
                componentes.Velocidad(random.uniform(-1, 1), random.uniform(-1, 1), 0, a_lo_largo_eje_mundo=True),
                componentes.CajaDelimitadora(componentes.Rectangulo3D(1.7, 1.7, 1.5)),
                componentes.ReporteColision(),
                componentes.ComponenteColision(),
                componentes.ObjetoFisico(),
                componentes.Casa(posicion=posicion, rotacion=glm.vec3(1.57, 0.0, 0.0)),
                componentes.Luz(atenuacion=glm.vec3(0.1, 0.0, 0.8), habilitado=(i < max_luces_gatos)),
                componentes.AnimacionLuz(color_base=glm.vec3(2.0, 0.0, 0.0), color_agregar=glm.vec3(0.5, 0.0, 0.0), factor_delta=random.uniform(0.8, 1.4))
            )
            
            # Agregar Esqueleto si está disponible
            esqueleto_gato = self.registro_modelos.obtener_esqueleto(recursos.GestorRecursos.GATO)
            if esqueleto_gato:
                self.add_component(self.gato, componentes.Esqueleto(esqueleto_gato))

        # Obtener textura del registro (cargada desde GLB)
        id_textura_queso = self.registro_modelos.obtener_textura(recursos.GestorRecursos.QUESO)
        color_queso = self.registro_modelos.obtener_color(recursos.GestorRecursos.QUESO)
        
        # Color por defecto si no se encuentra nada (amarillento)
        color_difuso = glm.vec3(1.0, 0.8, 0.0)
        if color_queso:
             color_difuso = glm.vec3(color_queso[0], color_queso[1], color_queso[2])

        self.objeto_victoria = self.create_entity(
            componentes.Modelo3D(self.registro_modelos.obtener_id(recursos.GestorRecursos.QUESO)),
            componentes.Transformacion(posicion=glm.vec3(self.laberinto.centro.x, self.laberinto.centro.y, 1.0), rotacion=glm.vec3(1.57, 0.0, 0.0), escala=glm.vec3(0.20, 0.20, 0.24)),
            componentes.MatrizTransformacion(),
            componentes.MaterialObjeto(difuso=color_difuso, id_textura=id_textura_queso),
            componentes.Victoria(),
            componentes.Velocidad(),
            componentes.CajaDelimitadora(componentes.Rectangulo3D(1.0, 1.0, 1.0)),
            componentes.ReporteColision(),
            componentes.Luz(atenuacion=glm.vec3(0.35, -0.36, 0.1)),
            componentes.AnimacionLuz(color_base=glm.vec3(1.0, 0.8, 0.0), color_agregar=glm.vec3(0.1, 0.1, 0.1))
        )
        
        # Agregar Esqueleto si está disponible
        esqueleto_queso = self.registro_modelos.obtener_esqueleto(recursos.GestorRecursos.QUESO)
        if esqueleto_queso:
            self.add_component(self.objeto_victoria, componentes.Esqueleto(esqueleto_queso))

        # --- Generar Nubes Fractales ---
        
        # Centro del laberinto (aprox 30.5, 30.5)
        centro_mapa_x = 30.5
        centro_mapa_y = 30.5
        
        # 1. Nubes de Horizonte (Bajas y lejanas)
        # Generar en un anillo exterior para asegurar que rodeen el mapa
        nubes_horizonte = 60
        radio_minimo = 50.0
        radio_maximo = 110.0
        
        for i in range(nubes_horizonte):
            angulo = random.uniform(0, math.pi * 2)
            distancia = random.uniform(radio_minimo, radio_maximo)
            
            pos_x = centro_mapa_x + math.cos(angulo) * distancia
            pos_y = centro_mapa_y + math.sin(angulo) * distancia
            
            # Altura baja para horizonte
            pos_z = random.uniform(-5.0, 10.0)
            escala = random.uniform(4.0, 9.0) # Un poco más grandes
            
            self._crear_nube(pos_x, pos_y, pos_z, escala)

    def _crear_nube(self, x, y, z, escala):
        self.create_entity(
            componentes.Modelo3D(self.registro_modelos.obtener_id(recursos.GestorRecursos.FRACTAL)),
            componentes.Transformacion(
                posicion=glm.vec3(x, y, z),
                rotacion=glm.vec3(random.random(), random.random(), random.random()),
                escala=glm.vec3(escala, escala, escala)
            ),
            componentes.MatrizTransformacion(),
            componentes.MaterialObjeto(difuso=glm.vec3(1.0, 1.0, 1.0)),
            componentes.Velocidad(a_lo_largo_eje_mundo=False) 
        )

    def recibir_dano(self):
        """Maneja la lógica cuando el jugador recibe daño"""
        self.vida -= 1

        if self.vida > 0:
            self.sonido.reproducir('daño')
            # Reiniciar posiciones
            self.reiniciar_posiciones()
            # Limpiar colisiones para evitar muerte instantánea al reaparecer
            for _id, colision in self.get_component(componentes.ReporteColision):
                colision.fallido.clear()
        else:
            self.sonido.pausar_musica()
            self.sonido.reproducir('daño')
            
            # Limpiar colisiones
            for _id, colision in self.get_component(componentes.ReporteColision):
                colision.fallido.clear()
                
            # Activar estado de derrota
            self.estado = recursos.ESTADO_DERROTA
            
            # Configurar cámara para la derrota (Igual que victoria)
            self.id_camara = self.cam_libre
            self.controles.permitir_cambio_camara = False
            self.controles.modo_control = recursos.ControlJuego.MODO_CAMARA_LIBRE
            
            # Crear ruta B-Spline alrededor del centro
            cx, cy = self.laberinto.centro.x, self.laberinto.centro.y
            radio = 25.0
            altura = 15.0
            
            # 8 Puntos de control formando un círculo
            puntos = []
            for i in range(8):
                angulo = (i / 8.0) * math.pi * 2
                x = cx + math.cos(angulo) * radio
                y = cy + math.sin(angulo) * radio
                z = altura + math.sin(angulo * 3) * 5.0 
                puntos.append(glm.vec3(x, y, z))
                
            self.curva_victoria = CurvaBSpline(puntos, cerrada=True)
                
            # Desactivar animación de victoria si estaba activa
            self.component_for_entity(self.objeto_victoria, componentes.AnimacionLuz).habilitado = False
            self.component_for_entity(self.objeto_victoria, componentes.Victoria).juego_terminado = True
            
            # Cambiar color de nubes a gris oscuro/negro (Tormenta)
            id_modelo_nube = self.registro_modelos.obtener_id(recursos.GestorRecursos.FRACTAL)
            for _id, (modelo, material) in self.get_components(componentes.Modelo3D, componentes.MaterialObjeto):
                if modelo.id_modelo == id_modelo_nube:
                    material.difuso = glm.vec3(0.2, 0.2, 0.25) # Gris azulado oscuro

    def toggle_vista_mapa(self):
        controles: recursos.ControlJuego = self.controles
        
        if controles.modo_control == recursos.ControlJuego.MODO_JUGADOR:
            # Cambiar a MODO MAPA (Vista superior estática)
            self.id_camara = self.cam_libre
            controles.modo_control = recursos.ControlJuego.MODO_MAPA
            
            # Posicionar cámara libre arriba del centro
            try:
                trans_cam_libre = self.component_for_entity(self.cam_libre, componentes.Transformacion)
                orient_cam_libre = self.component_for_entity(self.cam_libre, componentes.OrientacionCamara)
                
                # Centro del laberinto (aprox 30x30, centro en 15,15)
                # Altura 45 para ver todo
                trans_cam_libre.posicion = glm.vec3(15.0, 15.0, 45.0)
                
                # Mirar hacia abajo (Pitch -90 grados)
                # IMPORTANTE: SistemaOrientacionCamara usa trans.rotacion para calcular mirar_a.
                # Debemos setear la rotación explícitamente.
                trans_cam_libre.rotacion.x = -math.pi / 2.0
                trans_cam_libre.rotacion.z = 0.0
                
                # CAMBIO CRÍTICO: Cambiar vector 'Arriba' a Y (0, 1, 0) para evitar singularidad
                # al mirar hacia abajo en Z.
                orient_cam_libre.arriba = glm.vec3(0.0, 1.0, 0.0)
                
            except KeyError:
                pass

        elif controles.modo_control == recursos.ControlJuego.MODO_MAPA:
            # Volver a MODO JUGADOR
            self.id_camara = self.cam_jugador
            controles.modo_control = recursos.ControlJuego.MODO_JUGADOR
            
            # Restaurar vector 'Arriba' a Z (0, 0, 1) para la cámara libre (por si se usa en otro lado)
            try:
                orient_cam_libre = self.component_for_entity(self.cam_libre, componentes.OrientacionCamara)
                orient_cam_libre.arriba = glm.vec3(0.0, 0.0, 1.0)
            except KeyError:
                pass

    def reiniciar_posiciones(self):
        """Devuelve todas las entidades con componente Casa a su posición original"""
        for _id, (casa, transformacion, velocidad) in self.get_components(
                componentes.Casa,
                componentes.Transformacion,
                componentes.Velocidad):
            transformacion.posicion = casa.posicion
            transformacion.rotacion = casa.rotacion
            velocidad.valor = glm.vec3()

    def actualizar_resolucion(self, resolucion):
        self.resolucion = resolucion
        self.shader_estandar.actualizar_proyeccion(resolucion)
        
    def juego_ganado(self):
        self.sonido.reproducir('victoria')
        self.estado = recursos.ESTADO_VICTORIA
        
        # Configurar cámara para la victoria
        self.id_camara = self.cam_libre
        self.controles.modo_control = recursos.ControlJuego.MODO_CAMARA_LIBRE
        
        # Crear ruta B-Spline alrededor del centro
        cx, cy = self.laberinto.centro.x, self.laberinto.centro.y
        radio = 25.0
        altura = 15.0
        
        # 8 Puntos de control formando un círculo
        puntos = []
        for i in range(8):
            angulo = (i / 8.0) * math.pi * 2
            x = cx + math.cos(angulo) * radio
            y = cy + math.sin(angulo) * radio
            # Ondular un poco la altura
            z = altura + math.sin(angulo * 3) * 5.0 
            puntos.append(glm.vec3(x, y, z))
            
        self.curva_victoria = CurvaBSpline(puntos, cerrada=True)
