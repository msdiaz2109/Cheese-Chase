from OpenGL import GL as gl
import glm
import recursos

class ShaderBase:
    """Clase base para manejar la compilación y uso de shaders OpenGL"""
    def __init__(self):
        self.id_programa = gl.glCreateProgram()
        self.ids_componentes = []

    def liberar_recursos(self):
        """Elimina el programa y los shaders de la memoria de la GPU"""
        for id_shader in self.ids_componentes:
            gl.glDetachShader(self.id_programa, id_shader)
            gl.glDeleteShader(id_shader)
        gl.glDeleteProgram(self.id_programa)

    def _compilar_programa(self, codigo_vertice, codigo_fragmento, atributos=None):
        """Compila y enlaza los shaders de vértice y fragmento"""
        id_vertice = self._compilar_shader(codigo_vertice, gl.GL_VERTEX_SHADER)
        id_fragmento = self._compilar_shader(codigo_fragmento, gl.GL_FRAGMENT_SHADER)
        
        gl.glAttachShader(self.id_programa, id_vertice)
        gl.glAttachShader(self.id_programa, id_fragmento)
        
        if atributos:
            for nombre, indice in atributos.items():
                gl.glBindAttribLocation(self.id_programa, indice, nombre)
        
        gl.glLinkProgram(self.id_programa)
        if gl.glGetProgramiv(self.id_programa, gl.GL_LINK_STATUS) != gl.GL_TRUE:
            info = gl.glGetProgramInfoLog(self.id_programa)
            raise RuntimeError('Error al enlazar el programa: %s' % (info))
            
        self.ids_componentes.append(id_vertice)
        self.ids_componentes.append(id_fragmento)

    def _compilar_shader(self, codigo_fuente, tipo_shader):
        """Compila un shader individual"""
        id_shader = gl.glCreateShader(tipo_shader)
        gl.glShaderSource(id_shader, codigo_fuente)
        gl.glCompileShader(id_shader)
        if gl.glGetShaderiv(id_shader, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(id_shader)
            raise RuntimeError('Error de compilación del shader: %s' % (info))
        return id_shader

    def activar(self):
        """Activa el programa para su uso en el renderizado"""
        gl.glUseProgram(self.id_programa)

    def desactivar(self):
        """Desactiva el programa"""
        gl.glUseProgram(0)

class ShaderEstandar(ShaderBase):
    """Shader principal para renderizado 3D con iluminación y texturas"""
    
    # Constantes para atributos de vértices
    ATRIBUTO_POSICION = 0
    ATRIBUTO_NORMAL = 1
    ATRIBUTO_COORD_TEXTURA = 2
    ATRIBUTO_COLOR = 3
    ATRIBUTO_ARTICULACIONES = 4
    ATRIBUTO_PESOS = 5
    
    MAX_ARTICULACIONES = 64

    def __init__(self):
        super().__init__()
        atributos = {
            "position": self.ATRIBUTO_POSICION,
            "normal": self.ATRIBUTO_NORMAL,
            "textureCoords": self.ATRIBUTO_COORD_TEXTURA,
            "color": self.ATRIBUTO_COLOR,
            "jointIndices": self.ATRIBUTO_ARTICULACIONES,
            "weights": self.ATRIBUTO_PESOS
        }
        self._compilar_programa(
            self._obtener_codigo_vertice(),
            self._obtener_codigo_fragmento(),
            atributos)
            
        # Obtener ubicaciones de variables uniformes
        self.loc_matriz_transformacion = gl.glGetUniformLocation(self.id_programa, "transformationMatrix")
        self.loc_matriz_proyeccion = gl.glGetUniformLocation(self.id_programa, "projectionMatrix")
        self.loc_matriz_vista = gl.glGetUniformLocation(self.id_programa, "viewMatrix")
        
        # Luces
        self.loc_color_luz = []
        self.loc_posicion_luz = []
        self.loc_atenuacion_luz = []
        for i in range(recursos.ConfiguracionIluminacion.MAX_CONTEO_LUZ):
            self.loc_color_luz.append(gl.glGetUniformLocation(self.id_programa, f"lightColor[{i}]"))
            self.loc_posicion_luz.append(gl.glGetUniformLocation(self.id_programa, f"lightPosition[{i}]"))
            self.loc_atenuacion_luz.append(gl.glGetUniformLocation(self.id_programa, f"lightAttenuation[{i}]"))
            
        # Material
        self.loc_brillo = gl.glGetUniformLocation(self.id_programa, "shineDamper")
        self.loc_reflectividad = gl.glGetUniformLocation(self.id_programa, "reflectivity")
        self.loc_color_difuso = gl.glGetUniformLocation(self.id_programa, "diffuseColor")
        self.loc_ambiente_global = gl.glGetUniformLocation(self.id_programa, "globalAmbient")
        
        # Texturas
        self.loc_tiene_textura = gl.glGetUniformLocation(self.id_programa, "hasTexture")
        self.loc_sampler_textura = gl.glGetUniformLocation(self.id_programa, "textureSampler")
        self.loc_escala_uv = gl.glGetUniformLocation(self.id_programa, "uvScale")
        self.loc_usar_world_uv = gl.glGetUniformLocation(self.id_programa, "useWorldUV")
        
        # Animación (Skinning)
        self.loc_matrices_articulacion = gl.glGetUniformLocation(self.id_programa, "jointMatrices")
        self.loc_tiene_skinning = gl.glGetUniformLocation(self.id_programa, "hasSkinning")

    def activar(self):
        super().activar()
        gl.glUniform1i(self.loc_sampler_textura, 0)
        gl.glUniform3f(self.loc_escala_uv, 1.0, 1.0, 1.0)
        gl.glUniform1i(self.loc_usar_world_uv, 0)

    def set_usar_world_uv(self, usar):
        gl.glUniform1i(self.loc_usar_world_uv, 1 if usar else 0)

    def set_escala_uv(self, escala):
        gl.glUniform3f(self.loc_escala_uv, escala.x, escala.y, escala.z)

    def set_transformacion(self, matriz):
        gl.glUniformMatrix4fv(self.loc_matriz_transformacion, 1, gl.GL_FALSE, glm.value_ptr(matriz))

    def set_proyeccion(self, matriz):
        gl.glUniformMatrix4fv(self.loc_matriz_proyeccion, 1, gl.GL_FALSE, glm.value_ptr(matriz))

    def set_vista(self, matriz):
        gl.glUniformMatrix4fv(self.loc_matriz_vista, 1, gl.GL_FALSE, glm.value_ptr(matriz))

    def cargar_configuracion_luz(self, configuracion):
        """Carga la configuración de luces en el shader"""
        gl.glUniform3f(self.loc_ambiente_global, configuracion.ambiente_global.x, configuracion.ambiente_global.y, configuracion.ambiente_global.z)
        for i in range(recursos.ConfiguracionIluminacion.MAX_CONTEO_LUZ):
            if i < configuracion.conteo_luz:
                luz = configuracion.luces[i]
                pos = configuracion.posiciones_luz[i]
                gl.glUniform3f(self.loc_color_luz[i], luz.color.x, luz.color.y, luz.color.z)
                gl.glUniform3f(self.loc_posicion_luz[i], pos.x, pos.y, pos.z)
                gl.glUniform3f(self.loc_atenuacion_luz[i], luz.atenuacion.x, luz.atenuacion.y, luz.atenuacion.z)
            else:
                # Apagar luces no usadas
                gl.glUniform3f(self.loc_color_luz[i], 0, 0, 0)
                gl.glUniform3f(self.loc_posicion_luz[i], 0, 0, 0)
                gl.glUniform3f(self.loc_atenuacion_luz[i], 1, 0, 0)

    def set_material(self, material):
        """Configura el material del objeto actual"""
        gl.glUniform1f(self.loc_brillo, material.brillo)
        gl.glUniform3f(self.loc_reflectividad, material.especular.x, material.especular.y, material.especular.z)
        gl.glUniform3f(self.loc_color_difuso, material.difuso.x, material.difuso.y, material.difuso.z)
        
        if material.id_textura is not None:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, material.id_textura)
            gl.glUniform1i(self.loc_tiene_textura, 1)
        else:
            gl.glUniform1i(self.loc_tiene_textura, 0)

    def set_matrices_articulacion(self, matrices):
        """Sube las matrices de transformación de los huesos para animación"""
        conteo = min(len(matrices), self.MAX_ARTICULACIONES)
        if conteo > 0:
            # Aplanar lista de matrices para OpenGL
            datos_planos = []
            for m in matrices[:conteo]:
                datos_planos.extend([m[col][row] for col in range(4) for row in range(4)])
            
            gl.glUniformMatrix4fv(self.loc_matrices_articulacion, conteo, gl.GL_FALSE, (gl.GLfloat * len(datos_planos))(*datos_planos))

    def set_tiene_skinning(self, tiene_skinning):
        gl.glUniform1i(self.loc_tiene_skinning, 1 if tiene_skinning else 0)

    def actualizar_proyeccion(self, resolucion):
        """Recalcula y actualiza la matriz de proyección basada en la resolución"""
        self.activar()
        aspecto = resolucion[0] / resolucion[1]
        fov = 70
        cerca = 0.1
        lejos = 1000
        proyeccion = glm.perspective(glm.radians(fov), aspecto, cerca, lejos)
        self.set_proyeccion(proyeccion)
        self.desactivar()

    def _obtener_codigo_vertice(self):
        return """
        #version 400 core
        
        const int MAX_JOINTS = 64;
        const int MAX_WEIGHTS = 4;

        in vec3 position;
        in vec3 normal;
        in vec2 textureCoords;
        in vec3 color;
        in ivec4 jointIndices;
        in vec4 weights;

        out vec3 pass_surfaceNormal;
        out vec3 pass_toCameraVector;
        out vec3 pass_toLightVector[16];
        out vec2 pass_textureCoords;
        out vec3 pass_color;

        uniform mat4 transformationMatrix;
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform vec3 lightPosition[16];
        
        uniform mat4 jointMatrices[MAX_JOINTS];
        uniform int hasSkinning;
        uniform vec3 uvScale;
        uniform int useWorldUV;

        void main(void){
            vec4 worldPosition;
            vec4 totalLocalPos = vec4(0.0);
            vec4 totalNormal = vec4(0.0);
            
            if (hasSkinning == 1) {
                for(int i=0; i<MAX_WEIGHTS; i++){
                    mat4 jointTransform = jointMatrices[jointIndices[i]];
                    vec4 posePosition = jointTransform * vec4(position, 1.0);
                    totalLocalPos += posePosition * weights[i];
                    
                    vec4 worldNormal = jointTransform * vec4(normal, 0.0);
                    totalNormal += worldNormal * weights[i];
                }
                worldPosition = transformationMatrix * totalLocalPos;
                pass_surfaceNormal = (transformationMatrix * totalNormal).xyz;
            } else {
                worldPosition = transformationMatrix * vec4(position, 1.0);
                pass_surfaceNormal = (transformationMatrix * vec4(normal, 0.0)).xyz;
            }

            gl_Position = projectionMatrix * viewMatrix * worldPosition;

            if (useWorldUV == 1) {
                vec3 worldNormal = normalize((transformationMatrix * vec4(normal, 0.0)).xyz);
                vec3 absWorldNormal = abs(worldNormal);
                
                vec2 worldUV;
                if (absWorldNormal.z > 0.5) {
                    worldUV = worldPosition.xy;
                } else if (absWorldNormal.y > 0.5) {
                    worldUV = worldPosition.xz;
                } else {
                    worldUV = worldPosition.yz;
                }
                pass_textureCoords = worldUV * uvScale.x;
            } else {
                pass_textureCoords = textureCoords * uvScale.xy; 
            }
            
            pass_color = color;

            pass_toCameraVector = (inverse(viewMatrix) * vec4(0.0, 0.0, 0.0, 1.0)).xyz - worldPosition.xyz;

            for(int i=0; i<16; i++){
                pass_toLightVector[i] = lightPosition[i] - worldPosition.xyz;
            }
        }
        """

    def _obtener_codigo_fragmento(self):
        return """
        #version 400 core

        in vec3 pass_surfaceNormal;
        in vec3 pass_toCameraVector;
        in vec3 pass_toLightVector[16];
        in vec2 pass_textureCoords;
        in vec3 pass_color;

        out vec4 out_Color;

        uniform vec3 lightColor[16];
        uniform vec3 lightAttenuation[16];
        uniform float shineDamper;
        uniform vec3 reflectivity;
        uniform vec3 diffuseColor;
        uniform vec3 globalAmbient;
        
        uniform sampler2D textureSampler;
        uniform int hasTexture;

        void main(void){
            vec3 unitNormal = normalize(pass_surfaceNormal);
            vec3 unitVectorToCamera = normalize(pass_toCameraVector);

            vec3 totalDiffuse = vec3(0.0);
            vec3 totalSpecular = vec3(0.0);

            for(int i=0; i<16; i++){
                float distance = length(pass_toLightVector[i]);
                float attFactor = lightAttenuation[i].x + lightAttenuation[i].y * distance + lightAttenuation[i].z * distance * distance;
                vec3 unitLightVector = normalize(pass_toLightVector[i]);
                float nDotl = dot(unitNormal, unitLightVector);
                float brightness = max(nDotl, 0.0);
                vec3 lightDirection = -unitLightVector;
                vec3 reflectedLightDirection = reflect(lightDirection, unitNormal);
                float specularFactor = dot(reflectedLightDirection, unitVectorToCamera);
                specularFactor = max(specularFactor, 0.0);
                float dampedFactor = pow(specularFactor, shineDamper);
                totalDiffuse = totalDiffuse + (brightness * lightColor[i]) / attFactor;
                totalSpecular = totalSpecular + (dampedFactor * reflectivity * lightColor[i]) / attFactor;
            }
            totalDiffuse = max(totalDiffuse, globalAmbient);

            vec4 textureColor = vec4(1.0, 1.0, 1.0, 1.0);
            if (hasTexture == 1) {
                textureColor = texture(textureSampler, pass_textureCoords);
            }
            
            vec3 finalDiffuse = totalDiffuse * diffuseColor * pass_color * textureColor.rgb;

            out_Color = vec4(finalDiffuse + totalSpecular, 1.0);
        }
        """
