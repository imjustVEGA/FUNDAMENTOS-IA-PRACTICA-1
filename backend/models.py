from typing import Annotated, Literal
from pydantic import BaseModel, Field, model_validator

class Point(BaseModel):
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    lon: float = Field(ge=-180, le=180, allow_inf_nan=False)

class Region(Point):
    name: str
    weight: float = Field(gt=0, le=100, allow_inf_nan=False)
    radius_km: float = Field(default=300, gt=0, le=2000)

class Zone(Point):
    name: str
    radius_deg: float = Field(gt=0, le=180)
    active: bool = True
    kind: Literal['debris', 'object'] = 'debris'

class Scenario(BaseModel):
    name: str = 'Base'
    regions: Annotated[list[Region], Field(min_length=6, max_length=6)]
    zones: Annotated[list[Zone], Field(max_length=50)]
    footprint_km: float = Field(default=650, gt=0, le=5000)
    samples: int = Field(default=128, ge=16, le=512)

class Parameters(BaseModel):
    seed: int = Field(default=42, ge=0, le=2**32-1)
    population: int = Field(default=80, ge=8, le=200)
    generations: int = Field(default=120, ge=1, le=300)
    crossover: float = Field(default=.85, ge=0, le=1)
    mutation: float = Field(default=.25, ge=0, le=1)
    tournament: int = Field(default=3, ge=2, le=10)
    elite: int = Field(default=4, ge=1)
    attempts: int = Field(default=300, ge=1, le=1000)
    @model_validator(mode='after')
    def consistent(self):
        if self.elite >= self.population or self.tournament > self.population:
            raise ValueError('Élite y torneo deben ser compatibles con población')
        return self

Constellation = Annotated[list[Point], Field(min_length=8, max_length=8)]

class EvaluationRequest(BaseModel):
    configuration: Constellation
    scenario: Scenario

class OptimizeRequest(BaseModel):
    parameters: Parameters = Field(default_factory=Parameters)
    scenario: Scenario

class Coverage(BaseModel):
    name: str
    fraction: float
    covered: bool
    weight: float

class Evaluation(BaseModel):
    valid: bool
    status: Literal['valid', 'invalid', 'valid_insufficient']
    fitness: float
    covered_regions: int
    coverage: list[Coverage]
    violations: list[str]
    separation_deg: float

class Generation(BaseModel):
    generation: int
    best: float
    mean: float
    worst: float
    valid_count: int
    best_configuration: Constellation
    covered_regions: int

class Run(BaseModel):
    run_id: str | None = None
    status: Literal['success', 'no_feasible_found']
    message: str
    seed: int
    parameters: Parameters
    scenario: Scenario
    initial: Constellation | None = None
    final: Constellation | None = None
    initial_evaluation: Evaluation | None = None
    final_evaluation: Evaluation | None = None
    history: list[Generation] = Field(default_factory=list)

class ComparisonRequest(EvaluationRequest):
    previous_scenario: Scenario

class Comparison(BaseModel):
    before: Evaluation
    after: Evaluation

class ConfigurationPair(BaseModel):
    initial: Constellation | None
    final: Constellation | None
