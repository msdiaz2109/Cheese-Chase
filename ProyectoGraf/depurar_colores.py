import trimesh
import sys
import os
# Script para inspeccionar colores en modelos 3D
ruta_base = os.path.dirname(__file__)
archivo = os.path.join(ruta_base, "recursos", "gato.glb")
print(f"Inspeccionando {archivo}...")
try:
    # Cargar el archivo 3D
    datos = trimesh.load(archivo)
    
    modelo = None
    # Verificar si se cargó como una Escena (común en GLB) o una Malla directa
    if isinstance(datos, trimesh.Scene):
        print("Cargado como Escena")
        if len(datos.geometry) == 0:
            print("Sin geometría")
        else:
            print(f"Geometría encontrada: {len(datos.geometry)}")
            # Combinar todas las geometrías en una sola malla
            modelo = trimesh.util.concatenate(tuple(datos.geometry.values()))
            print("Modelo combinado creado")
    else:
        print("Cargado como Malla")
        modelo = datos
    if modelo:
        print(f"El modelo tiene {len(modelo.vertices)} vértices y {len(modelo.faces)} caras")
        
        # Verificar colores
        # Verificar si existen colores guardados en los vértices
        colores_vertice = hasattr(modelo.visual, 'vertex_colors') and modelo.visual.vertex_colors is not None and len(modelo.visual.vertex_colors) > 0
        # Verificar si existen colores guardados en las caras (polígonos)
        colores_cara = hasattr(modelo.visual, 'face_colors') and modelo.visual.face_colors is not None and len(modelo.visual.face_colors) > 0
        
        print(f"Tiene colores de vértice: {colores_vertice}")
        if colores_vertice:
            print(f"Forma: {modelo.visual.vertex_colors.shape}")
            print(f"Muestra: {modelo.visual.vertex_colors[:5]}")
            
        print(f"Tiene colores de cara: {colores_cara}")
        if colores_cara:
            print(f"Forma: {modelo.visual.face_colors.shape}")
            print(f"Muestra: {modelo.visual.face_colors[:5]}")
            
except Exception as e:
    print(f"Error: {e}")
