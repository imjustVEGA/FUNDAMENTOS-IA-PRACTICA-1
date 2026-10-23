# Análisis de ejecuciones reales

Generado por `python -m scripts.experiments`. Parámetros completos, escenarios y 121 generaciones por ejecución están en results/integration/*.json. Cinco semillas: 42, 7, 19, 73, 101. Desviación estándar poblacional (ddof=0).

Base semilla 42: fitness 0.000000 → 100.000000; mejora absoluta 100.000000 puntos. Regiones suficientes: 6/6. Sin cubrir: ninguna. Violaciones finales: 0.

Base, cinco semillas: media 98.461538, desviación 3.076923, mínimo 92.307692, máximo 100.000000. Sin mutación: media 95.336538, desviación 5.874205. La diferencia observada es 3.125000 puntos; cinco semillas no bastan para generalizar causalidad. Ambos tratamientos comparten semillas e inicialización. La mutación introduce posiciones que la cruza por sí sola no puede crear.

Espacio reducido: media 48.009615, desviación 1.789753, cobertura media 3.00/6. La solución base bajo las nuevas zonas es válida: False. Reoptimizar alcanza 48.365385 en semilla 42. La restricción total retorna no_feasible_found sin soluciones falsas; 180° prueba imposibilidad en este modelo. Otros fallos acotados no la prueban.

Cambio de prioridades sobre el escenario reducido: solución anterior reevaluada 30.875000; nueva búsqueda 52.958333. No se afirma mejora si la ejecución no la produce. Comparar sólo fitness entre pesos diferentes carece de sentido: ambas cifras anteriores usan los pesos nuevos.

Una puntuación 100 prueba el máximo de este fitness discretizado, pero no una constelación orbital óptima. Las regiones pequeñas y ocho huellas grandes facilitan saturación. No se recompensa el área fuera de las regiones, ni existe redundancia temporal, combustible o riesgo dinámico. El desempate por separación mejora dispersión sin sacrificar fitness. Las gráficas provienen de estas ejecuciones y no fueron suavizadas ni modificadas.
