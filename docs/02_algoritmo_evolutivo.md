# Algoritmo evolutivo · Integrante 1

Motor independiente de HTTP en backend/evolution.py. Un cromosoma es una matriz 8×2. Generador NumPy default_rng con semilla explícita. El primer individuo se obtiene uniformemente sobre la esfera (longitud uniforme, seno de latitud uniforme). La mitad de los individuos restantes recibe posiciones perturbadas cerca de regiones elegidas al azar. Esto aporta información del problema pero no asigna una solución completa.

Cada generación evalúa fitness y separación mínima. Torneos sin reemplazo eligen progenitores; gana el mayor fitness y después la mayor separación mínima. Cruza uniforme por pares completos lat/lon, con probabilidad 0.85 por hijo. Mutación por satélite con probabilidad 0.25: en 15% de esas mutaciones se reinicia el punto uniformemente; en el resto, perturbación gaussiana tangencial con σ=5°. El operador tangencial normaliza sobre la esfera y evita recortar coordenadas en los polos.

Se conservan cuatro élites sin cambio. Sólo se admiten hijos reparados válidos. La reparación intenta hasta 300 puntos uniformes por posición inválida. La generación intenta hasta 3(P−E) hijos, luego completa con copias de la mejor solución válida. La inicialización aborta si no puede reparar un individuo dentro del presupuesto. Esta elección conservadora puede fallar aunque exista espacio factible; se reporta explícitamente.

Población 80, 120 generaciones, torneo 3 y semilla 42 por defecto. Todos editables y validados. La condición de parada normal es exactamente el máximo de generaciones; no se detiene al alcanzar 100 para estudiar diversidad por desempate. No hay garantía de convergencia global. La generación 0 registra la población inicial completa y las siguientes 120 registran sus descendientes.

El historial guarda máximo, media, mínimo, número válido, mejor configuración y regiones suficientes por generación. La referencia individual aleatoria se compara con el resultado final; no se confunde con el mejor individuo de generación 0. El elitismo garantiza máximo no decreciente; la media y el mínimo pueden bajar. No hay curvas prefabricadas.
