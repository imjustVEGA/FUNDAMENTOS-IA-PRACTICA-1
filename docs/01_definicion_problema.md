# Modelo matemático previo a la implementación

AstroShield educativo optimiza una instantánea de ocho puntos subsatelitales C∈([-90,90]×[-180,180])⁸. La Tierra es esférica (6371 km); la altitud ilustrativa de 550 km sólo afecta al dibujo. No se simulan órbitas, velocidades, sensores, tiempo ni dinámica de desechos. Es independiente de SATCAT y NEO.

La distancia angular es atan2(||u×v||,u·v) entre vectores unitarios; para cálculos masivos se usa arccos del producto escalar recortado a [-1,1]. Evita discontinuidades del antimeridiano y singularidades polares. La distancia superficial es Rθ.

Cada región es un disco esférico de 300 km. Se discretiza con 128 puntos deterministas de área uniforme: cos(θᵢ)=1−((i+0.5)/128)(1−cos(300/R)), azimut iπ(3−√5). Es una estimación numérica reproducible, no cobertura física exacta. Se cubre una muestra si está a ≤650 km de al menos un satélite. La unión evita contar dos veces. Se reporta la fracción exacta de muestras, y se considera suficiente si es ≥0.8.

F=100[0.8Σwᵣcᵣ/Σwᵣ+0.2Σwᵣ1(cᵣ≥0.8)/Σwᵣ]. Está entre 0 y 100. Pesos iniciales 3,3,2,2,2,1 dan mayor importancia a las regiones altas sin excluir las demás. Son preferencias educativas editables. Los saltos del umbral y la discretización limitan la sensibilidad. Se desempata por distancia mínima entre satélites, sin alterar F. No se impone separación física adicional.

Las cinco exclusiones son discos angulares cerrados: su borde también está prohibido. Todas las soluciones aceptadas deben ser factibles. Se reparan puntos inválidos con intentos acotados, se rechaza un individuo si falla la reparación y se limita el presupuesto total. No encontrar factibilidad no demuestra imposibilidad. Una zona activa de 180° sí constituye una prueba directa de imposibilidad del modelo.

La referencia inicial es un individuo uniforme aleatorio válido, conservado como candidato y comparable con el resultado final. La población mezcla individuos aleatorios y sesgados hacia regiones, nunca usa una solución final predefinida. Los parámetros, muestras, semilla y escenarios se guardan para reproducibilidad.
