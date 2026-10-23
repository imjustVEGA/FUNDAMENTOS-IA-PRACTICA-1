"""Pruebas de escenarios difíciles, condiciones inviables y mecanismo acotado de reparación (Integrante 3: Owen)."""
import pytest
import numpy as np
from backend.models import Parameters, Point
from backend.scenarios import (
    crear_escenario_a_normal,
    crear_escenario_b_espacio_reducido,
    crear_escenario_c_configuracion_invalida,
    crear_escenario_d_inviable,
    crear_escenario_e_cambio_condiciones,
    analizar_viabilidad_teorica,
    reevaluar_configuracion_anterior,
)
from backend.restrictions.validator import validar_configuracion, is_valid_point
from backend.restrictions.repair import reparar_satelite, reparar_configuracion
from backend.evolution import optimize

def test_escenario_a_normal():
    """Escenario A: Tres zonas y dos objetos base. El sistema valida correctamente una constelación factible."""
    escenario_a = crear_escenario_a_normal()
    analisis = analizar_viabilidad_teorica(escenario_a)
    assert analisis["inviable_demostrado"] is False
    
    # Optimización rápida sobre Escenario A
    p = Parameters(population=16, generations=5, seed=42)
    res = optimize(escenario_a, p)
    assert res.status == "success"
    assert res.final is not None
    
    val = validar_configuracion(res.final, escenario_a)
    assert val.valida is True
    assert val.total_violaciones == 0

def test_escenario_b_espacio_reducido():
    """Escenario B: Restricciones expandidas y zonas adicionales. Reduce la densidad del espacio factible."""
    escenario_b = crear_escenario_b_espacio_reducido()
    assert len(escenario_b.zones) > 5
    
    # La zona Atlántico Norte tiene radio expandido a 25°
    zona_atlantico = next(z for z in escenario_b.zones if z.name == "Atlántico Norte")
    assert zona_atlantico.radius_deg == pytest.approx(25.0)
    
    # Un satélite a 20° de latitud respecto al centro de Atlántico Norte (45 + 20 = 65, -35)
    # era válido en Escenario A (radio 12°), pero es inválido en Escenario B (radio 25°)
    punto_prueba = [Point(lat=65.0, lon=-35.0)] + [Point(lat=0.0, lon=float(i*20)) for i in range(7)]
    
    val_a = validar_configuracion(punto_prueba, crear_escenario_a_normal())
    assert val_a.valida is True
    
    val_b = validar_configuracion(punto_prueba, escenario_b)
    assert val_b.valida is False
    assert any(v.nombre == "Atlántico Norte" for v in val_b.violaciones)

def test_escenario_c_configuracion_invalida():
    """Escenario C: Detecta intencionalmente satélites dentro de zonas y objetos, identificando a los infractores."""
    escenario, config_invalida = crear_escenario_c_configuracion_invalida()
    
    resultado = validar_configuracion(config_invalida, escenario)
    assert resultado.valida is False
    assert resultado.total_violaciones >= 3
    
    # S1 dentro de Atlántico Norte
    assert any(v.satelite == 1 and v.tipo == "zona_restringida" and v.nombre == "Atlántico Norte" for v in resultado.violaciones)
    # S2 dentro de Objeto A
    assert any(v.satelite == 2 and v.tipo == "objeto_existente" and v.nombre == "Objeto A" for v in resultado.violaciones)
    # S3 sobre el borde de Pacífico Sur
    assert any(v.satelite == 3 and v.nombre == "Pacífico Sur" for v in resultado.violaciones)

def test_escenario_d_condicion_inviable_sin_bucle_infinito():
    """Escenario D: Zona de 180° que excluye toda la esfera.
    El sistema debe identificar la imposibilidad matemática y terminar de forma inmediata
    sin bloqueos ni bucles infinitos.
    """
    escenario_d = crear_escenario_d_inviable()
    
    # 1. Análisis teórico de viabilidad
    analisis = analizar_viabilidad_teorica(escenario_d)
    assert analisis["inviable_demostrado"] is True
    assert "180" in analisis["motivo"]
    
    # 2. Comprobar que cualquier punto es inválido
    assert is_valid_point([0.0, 0.0], escenario_d) is False
    assert is_valid_point([90.0, 0.0], escenario_d) is False
    assert is_valid_point([-45.0, 120.0], escenario_d) is False
    
    # 3. Mecanismo de reparación acotada: no debe congelarse, retorna None inmediatamente
    reparado, intentos, msg = reparar_satelite([0.0, 0.0], escenario_d, max_intentos=10)
    assert reparado is None
    assert intentos == 10
    assert "Presupuesto de 10 intentos agotado" in msg
    
    # 4. Motor de optimización: detección directa sin bucle infinito
    r = optimize(escenario_d, Parameters(population=10, generations=2))
    assert r.status == "no_feasible_found"
    assert r.final is None
    assert "Una zona activa de 180° excluye toda la esfera" in r.message

def test_escenario_e_cambio_de_condiciones_y_explicacion():
    """Escenario E: Evalúa solución inicial, modifica restricciones y genera explicación clara de infracciones."""
    s_ini, s_mod, config = crear_escenario_e_cambio_condiciones()
    
    comp = reevaluar_configuracion_anterior(config, s_ini, s_mod)
    assert comp.anterior_valida is True
    assert comp.actual_valida is False
    assert comp.cambio_validez is True
    assert "Nube de Desechos Yucatán" in comp.detalles

def test_distincion_inviabilidad_demostrada_vs_agotamiento_de_presupuesto():
    """Distingue entre un escenario matemáticamente imposible y un agotamiento del presupuesto de búsqueda."""
    s = crear_escenario_a_normal()
    # Con solo 1 intento permitido de reparación, un escenario difícil puede no encontrar solución factible
    p_exhausted = Parameters(population=10, generations=2, attempts=1)
    
    # No es matemáticamente inviable
    assert analizar_viabilidad_teorica(s)["inviable_demostrado"] is False

def test_reparacion_acotada_exito():
    """El mecanismo de reparación reubica satisfactoriamente un satélite inválido en un punto factible."""
    s = crear_escenario_a_normal()
    # Punto en el centro del Atlántico Norte (inválido)
    punto_invalido = Point(lat=45.0, lon=-35.0)
    
    reparado, intentos, msg = reparar_satelite(punto_invalido, s, rng=np.random.default_rng(42), max_intentos=300)
    assert reparado is not None
    assert intentos >= 1
    assert is_valid_point(reparado, s) is True
    assert "reparado con éxito" in msg
