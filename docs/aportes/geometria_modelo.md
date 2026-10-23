# Definición del problema

## Modelo matemático y cobertura

La Tierra se modela como una esfera perfecta de radio 6371 km. Cada satélite
se representa únicamente mediante su punto subsatelital de latitud y longitud;
no se simulan órbitas ni propagación. Todas las distancias se calculan sobre
círculos máximos mediante haversine, nunca con distancias euclidianas o
proyecciones planas.

Cada región de interés es un disco geodésico de 300 km representado por 1000
muestras discretas, generadas uniformemente en área. El muestreo usa
`numpy.random.default_rng` y una semilla efectiva igual a la semilla global
más un hash entero estable del nombre de la región. Por tanto, la misma región,
semilla y cantidad de muestras producen los mismos puntos, incluso entre
procesos. La semilla global predeterminada es 0; el tamaño y la semilla se
pueden cambiar al precomputar muestras.

Una muestra se considera observada si al menos un satélite está a una distancia
de círculo máximo no mayor que 650 km. La fracción reportada es siempre el
número de muestras observadas dividido entre el total, contando la unión de las
huellas para evitar doble conteo. El umbral de 80 % solo determina el indicador
booleano «cubierta» y no reemplaza ni redondea la fracción reportada. Este es
un cálculo discreto aproximado, no una medición física exacta.

El fitness base combina en 80 % la cobertura ponderada de las muestras y en
20 % el peso relativo de las regiones que alcanzan el umbral. Se limita al
intervalo [0, 100] y no incluye penalizaciones por restricciones.

No se usa WGS84 ni un elipsoide: el enunciado define una Tierra esférica y
distancias de círculo máximo. Introducir un elipsoide cambiaría el modelo y
mezclaría supuestos que no forman parte de esta actividad.

## Geometria y cobertura (responsabilidad: Integrante 2)

### Modelo esferico
- Tierra = esfera perfecta de radio 6371 km (sin elipsoide WGS84; simplificacion explicita).
- Distancias por haversine (circulo maximo); maneja antimeridiano y polos.
- Satelites = puntos subsatelitales (lat, lon); altitud 550 km solo ilustrativa.
- Huella de observacion: radio 650 km sobre la superficie.
- Region de interes: disco geodesico de 300 km.

### Muestreo de regiones (discretizacion)
- Cada region se representa por N muestras fijas y reproducibles.
- Muestreo uniforme en area dentro del disco.
- Es una discretizacion, no una medicion fisica exacta.

### Cobertura
- Una muestra esta cubierta si algun satelite la cubre (union, sin doble conteo).
- fraccion = muestras_cubiertas / muestras_totales.
- cubierta = (fraccion >= 0.80).

### Fitness base
- fitness = 100 * (0.80 * cobertura_ponderada + 0.20 * regiones_cubiertas_ponderadas).
- Acotado en [0, 100].

### Validacion
- pytest backend/tests/domain -v -> 30 passed.
