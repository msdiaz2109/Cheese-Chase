import glm

def hsv_a_rgb(h, s, v):
    """
    Convierte un color de modelo HSV a RGB.
    
    Parámetros:
    h (float): Matiz (Hue) [0.0 - 360.0]
    s (float): Saturación [0.0 - 1.0]
    v (float): Valor (Brillo) [0.0 - 1.0]
    
    Retorna:
    glm.vec3: Color en formato RGB con valores entre 0.0 y 1.0
    """
    c = v * s
    x = c * (1 - abs(((h / 60.0) % 2) - 1))
    m = v - c
    
    r_temp, g_temp, b_temp = 0.0, 0.0, 0.0
    
    if 0 <= h < 60:
        r_temp, g_temp, b_temp = c, x, 0
    elif 60 <= h < 120:
        r_temp, g_temp, b_temp = x, c, 0
    elif 120 <= h < 180:
        r_temp, g_temp, b_temp = 0, c, x
    elif 180 <= h < 240:
        r_temp, g_temp, b_temp = 0, x, c
    elif 240 <= h < 300:
        r_temp, g_temp, b_temp = x, 0, c
    elif 300 <= h < 360:
        r_temp, g_temp, b_temp = c, 0, x
        
    return glm.vec3(r_temp + m, g_temp + m, b_temp + m)

def rgb_a_cmy(r, g, b):
    """
    Convierte RGB a CMY.
    """
    return glm.vec3(1.0 - r, 1.0 - g, 1.0 - b)
