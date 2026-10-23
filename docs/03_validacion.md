# Validación y experimentación

`python -m pytest -q` prueba geometría, antimeridiano, ambos polos, mutación, muestreo, unión de huellas, cobertura parcial, cinco exclusiones y sus bordes, desactivación, elitismo, semilla, serialización, errores de entrada y endpoints. La exclusión completa se detecta directamente; otra casi completa consume intentos acotados y retorna fallo de búsqueda.

`python -m scripts.experiments` ejecuta los nueve escenarios solicitados y escribe 21 JSON completos, CSV, estadísticas y cuatro figuras. Base, sin mutación, espacio reducido y prioridad nueva tienen cinco semillas cada uno; imposible tiene una. Población y generaciones por defecto (80/120). Las pruebas 1–4 se comprueban con ejecución base e invariantes; 5 usa tres exclusiones adicionales de 7° centradas en Yucatán, Amazonía y California; 6 añade una exclusión de 180°; 7 compara cinco semillas; 8 elimina mutación con la misma inicialización; 9 eleva el peso de Yucatán a 20 sobre el escenario reducido y reevalúa la solución previa bajo el mismo criterio nuevo.

Cada JSON conserva parámetros, regiones, pesos, restricciones, semilla, posiciones iniciales y finales, cobertura y todas las generaciones. summary.csv permite comparar sin leer los cromosomas. statistics.json incluye media, desviación poblacional, mínimo, máximo y reevaluaciones de la misma solución. Las figuras se regeneran desde los resultados obtenidos en el mismo script.

No se exige que cada semilla produzca 100, ni que quitar mutación siempre empeore. Revisar distribución y limitaciones antes de concluir. La UI admite cambiar escenarios, revalidar y volver a optimizar. La validez de una configuración es independiente de que logre cobertura suficiente.
