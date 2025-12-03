import glm

class CurvaBezier:
    """Clase para crear movimientos curvos suaves (Curva de Bézier Cúbica)"""
    
    def __init__(self, punto_inicio, control_1, control_2, punto_final):
        self.inicio = punto_inicio
        self.control_1 = control_1
        self.control_2 = control_2
        self.final = punto_final

    def calcular_punto(self, tiempo):
        """
        Calcula una posición en la curva basada en el tiempo (0.0 a 1.0)
        Fórmula: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
        """
        # Inverso del tiempo (lo que falta para terminar)
        t = tiempo
        u = 1 - t
        
        # Potencias para la fórmula
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        # Calcular la posición final sumando las influencias de cada punto
        # 1. Influencia del punto de inicio (disminuye rápido)
        parte_inicio = uuu * self.inicio
        
        # 2. Influencia del primer control (sube y baja al principio)
        parte_control_1 = 3 * uu * t * self.control_1
        
        # 3. Influencia del segundo control (sube y baja al final)
        parte_control_2 = 3 * u * tt * self.control_2
        
        # 4. Influencia del punto final (aumenta rápido al final)
        parte_final = ttt * self.final

        return parte_inicio + parte_control_1 + parte_control_2 + parte_final
