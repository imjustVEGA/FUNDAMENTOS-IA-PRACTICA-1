import { baseScenario, getPresetScenarios } from '../engine/scenarios';
import { optimize } from '../engine/evolution';
import { Evaluator } from '../engine/coverage';
import type { Scenario, Parameters, Run, Comparison, Evaluation, Point } from '../types';

const storedRuns: Record<string, Run> = {};

export async function api<T>(path: string, body?: unknown): Promise<T> {
  const cleanPath = path.replace(/^\/?(api\/)?/, '');

  if (cleanPath === 'scenario') {
    return baseScenario() as unknown as T;
  }

  if (cleanPath === 'scenarios') {
    return getPresetScenarios() as unknown as T;
  }

  if (cleanPath === 'optimize') {
    const { parameters, scenario } = (body || {}) as {
      parameters: Parameters;
      scenario: Scenario;
    };
    const run = optimize(scenario, parameters);
    const runId = Math.random().toString(36).substring(2, 10);
    run.run_id = runId;
    storedRuns[runId] = run;
    return run as unknown as T;
  }

  if (cleanPath === 'compare') {
    const { configuration, previous_scenario, scenario } = (body || {}) as {
      configuration: Point[];
      previous_scenario: Scenario;
      scenario: Scenario;
    };
    const prevEval = new Evaluator(previous_scenario).evaluate(configuration);
    const nextEval = new Evaluator(scenario).evaluate(configuration);
    const comparison: Comparison = { before: prevEval, after: nextEval };
    return comparison as unknown as T;
  }

  if (cleanPath === 'evaluate' || cleanPath === 'validate') {
    const { configuration, scenario } = (body || {}) as {
      configuration: Point[];
      scenario: Scenario;
    };
    const evalResult = new Evaluator(scenario).evaluate(configuration);
    return evalResult as unknown as T;
  }

  if (cleanPath.startsWith('runs/')) {
    const runId = cleanPath.split('/')[1];
    if (storedRuns[runId]) {
      return storedRuns[runId] as unknown as T;
    }
  }

  // Fallback si estuviera disponible un backend
  try {
    const r = await fetch('/api/' + path, body ? {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    } : undefined);
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`API ${r.status}: ${text.slice(0, 350)}`);
    }
    return r.json();
  } catch (err) {
    throw err;
  }
}
