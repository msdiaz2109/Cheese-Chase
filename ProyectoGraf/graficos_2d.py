from OpenGL import GL as gl
import glm
from graficos_3d import ShaderBase

class ShaderUI(ShaderBase):
    """Shader para renderizado de interfaz de usuario 2D (sin iluminación)"""
    
    ATRIBUTO_POSICION = 0
    ATRIBUTO_COORD_TEXTURA = 1

    def __init__(self):
        super().__init__()
        atributos = {
            "position": self.ATRIBUTO_POSICION,
            "textureCoords": self.ATRIBUTO_COORD_TEXTURA
        }
        self._compilar_programa(
            self._obtener_codigo_vertice(),
            self._obtener_codigo_fragmento(),
            atributos)
        
        self.loc_matriz_transformacion = gl.glGetUniformLocation(self.id_programa, "transformationMatrix")
        self.loc_sampler_textura = gl.glGetUniformLocation(self.id_programa, "textureSampler")

    def activar(self):
        super().activar()
        gl.glUniform1i(self.loc_sampler_textura, 0)

    def set_transformacion(self, matriz):
        gl.glUniformMatrix4fv(self.loc_matriz_transformacion, 1, gl.GL_FALSE, glm.value_ptr(matriz))

    def _obtener_codigo_vertice(self):
        return """
        #version 400 core

        in vec2 position;
        in vec2 textureCoords;

        out vec2 pass_textureCoords;

        uniform mat4 transformationMatrix;

        void main(void){
            gl_Position = transformationMatrix * vec4(position, 0.0, 1.0);
            pass_textureCoords = textureCoords;
        }
        """

    def _obtener_codigo_fragmento(self):
        return """
        #version 400 core

        in vec2 pass_textureCoords;

        out vec4 out_Color;

        uniform sampler2D textureSampler;

        void main(void){
            out_Color = texture(textureSampler, pass_textureCoords);
            if (out_Color.a < 0.1) {
                discard;
            }
        }
        """
