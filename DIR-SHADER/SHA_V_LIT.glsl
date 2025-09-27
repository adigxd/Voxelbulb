#version 330 core

layout (location = 0) in vec3 POS; // Vertex position attribute
layout (location = 1) in float FRC_COL_LAY;
layout (location = 2) in float FRC_COL_CHK_AVG_LAY;
layout (location = 3) in vec3 NML_LAY; // normal vector for light

flat out float Y; // to fragment shader
flat out float X; // to fragment shader
flat out float Z; // to fragment shader

out float FRC_COL;
out float FRC_COL_CHK_AVG;
out vec3 POS_SHA_F; // vertex position to world space for fragment shader
out vec3 NML; // normal vector for light

uniform mat4 model;      // Model transformation
uniform mat4 view;       // Camera view transformation
uniform mat4 projection; // Perspective projection

void main()
{
    Y = floor(POS.y);
    X = floor(POS.x);
    Z = floor(POS.z);
	
	POS_SHA_F = vec3(model * vec4(POS, 1.0));
	NML = mat3(transpose(inverse(model))) * NML_LAY; // transform normal (idk)
	
	FRC_COL = FRC_COL_LAY;
	FRC_COL_CHK_AVG = FRC_COL_CHK_AVG_LAY;

    gl_Position = projection * view * model * vec4(POS, 1.0); // transform vertex
}
