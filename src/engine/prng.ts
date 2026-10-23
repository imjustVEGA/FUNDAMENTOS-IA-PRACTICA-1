/**
 * Generador de números pseudoaleatorios determinista con soporte de semilla.
 * Equivalente al RNG estándar para simulaciones reproducibles.
 */
export class PRNG {
  private s: number;

  constructor(seed: number = 42) {
    this.s = (seed >>> 0) || 1;
  }

  /** Retorna número en [0, 1) */
  random(): number {
    let t = (this.s += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  /** Retorna número uniforme en [min, max) */
  uniform(min: number, max: number): number {
    return min + (max - min) * this.random();
  }

  /** Retorna entero aleatorio en [0, max) */
  integers(max: number): number {
    return Math.floor(this.random() * max);
  }

  /**
   * Genera distribución normal estándar N(mean, std) mediante Box-Muller
   */
  normal(mean: number = 0, std: number = 1): number {
    let u1 = this.random();
    let u2 = this.random();
    while (u1 <= 1e-15) u1 = this.random();
    const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    return mean + z0 * std;
  }

  /** Selecciona n elementos únicos sin reemplazo de un array de longitud size */
  choice(size: number, count: number): number[] {
    const pool = Array.from({ length: size }, (_, i) => i);
    const chosen: number[] = [];
    for (let i = 0; i < count; i++) {
      const idx = this.integers(pool.length);
      chosen.push(pool[idx]);
      pool.splice(idx, 1);
    }
    return chosen;
  }
}
