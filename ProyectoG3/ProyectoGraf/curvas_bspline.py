import glm

class CurvaBSpline:
    """
    Implementación de una curva B-Spline Cúbica Uniforme.
    Ideal para trayectorias suaves y cíclicas de cámara.
    """
    def __init__(self, puntos_control, cerrada=False):
        self.puntos = puntos_control
        self.cerrada = cerrada
        
    def calcular_punto(self, t_total):
        """
        Calcula un punto en la spline.
        t_total: valor entre 0.0 y 1.0 que representa el recorrido completo de la curva.
        """
        num_puntos = len(self.puntos)
        if num_puntos < 4:
            return glm.vec3(0) # Se necesitan al menos 4 puntos
            
        # Si es cerrada, el recorrido incluye volver al inicio
        # Ajustamos el índice base
        if self.cerrada:
            t_escalado = t_total * num_puntos
            indice = int(t_escalado)
            t = t_escalado - indice
            
            # Índices de los 4 puntos de control necesarios para este segmento
            i0 = (indice - 1) % num_puntos
            i1 = indice % num_puntos
            i2 = (indice + 1) % num_puntos
            i3 = (indice + 2) % num_puntos
        else:
            # Para abierta, ajustamos para no salirnos de rango
            # (Implementación simplificada para el caso de uso de cámara cíclica)
            # Para este proyecto usaremos principalmente el modo cerrado para la cámara
            t_escalado = t_total * (num_puntos - 3)
            indice = int(t_escalado)
            t = t_escalado - indice
            
            i0 = max(0, min(indice, num_puntos - 1))
            i1 = max(0, min(indice + 1, num_puntos - 1))
            i2 = max(0, min(indice + 2, num_puntos - 1))
            i3 = max(0, min(indice + 3, num_puntos - 1))

        p0 = self.puntos[i0]
        p1 = self.puntos[i1]
        p2 = self.puntos[i2]
        p3 = self.puntos[i3]

        # Polinomios base de B-Spline cúbica uniforme
        # 1/6 * [ (-t^3 + 3t^2 - 3t + 1)P0 + (3t^3 - 6t^2 + 4)P1 + (-3t^3 + 3t^2 + 3t + 1)P2 + (t^3)P3 ]
        
        tt = t * t
        ttt = tt * t
        
        term0 = (-ttt + 3*tt - 3*t + 1) / 6.0
        term1 = (3*ttt - 6*tt + 4) / 6.0
        term2 = (-3*ttt + 3*tt + 3*t + 1) / 6.0
        term3 = ttt / 6.0
        
        return p0 * term0 + p1 * term1 + p2 * term2 + p3 * term3
