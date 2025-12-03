import trimesh
import os
from PIL import Image
# Script para extraer texturas de archivos GLB
def extraer_textura(archivo, ruta_salida):
    try:
        # Cargar el modelo
        datos = trimesh.load(archivo)
        textura = None
        
        # Buscar la textura en la escena o malla
        if isinstance(datos, trimesh.Scene):
            for geometria in datos.geometry.values():
                if hasattr(geometria.visual, 'material') and hasattr(geometria.visual.material, 'baseColorTexture'):
                    textura = geometria.visual.material.baseColorTexture
                    break
        else:
            if hasattr(datos.visual, 'material') and hasattr(datos.visual.material, 'baseColorTexture'):
                textura = datos.visual.material.baseColorTexture
        if textura:
            # Guardar la imagen encontrada
            textura.save(ruta_salida)
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    ruta_base = os.path.dirname(__file__)
    ruta_recursos = os.path.join(ruta_base, "recursos")
    os.makedirs(ruta_recursos, exist_ok=True)
    
    archivo = os.path.join(ruta_recursos, "raton.glb")
    ruta_salida = os.path.join(ruta_recursos, "Feldmaus_Diffuse.png")
    
    extraer_textura(archivo, ruta_salida)
