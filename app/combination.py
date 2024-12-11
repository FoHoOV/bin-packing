from pydantic import ValidationError
from pyomo.environ import (
    ConcreteModel,
    Var,
    Objective,
    Constraint,
    NonNegativeReals,
    Binary,
    SolverFactory,
    quicksum,
)

from models.combination import Item


def solve_knapsack(items: list[Item], target_sum: float) -> list[Item]:
    model = ConcreteModel()

    model.I = range(len(items))
    model.x = Var(model.I, domain=Binary)

    # Introduce variables for difference
    model.diff_plus = Var(domain=NonNegativeReals)
    model.diff_minus = Var(domain=NonNegativeReals)

    # sum(weights[i]*x[i]) - target_sum = diff_plus - diff_minus
    model.sum_constraint = Constraint(
        expr=quicksum(items[i].weight * model.x[i] for i in model.I) - target_sum
        == model.diff_plus - model.diff_minus
    )

    # Large M to enforce lexicographic-like priority
    M = sum(it.weight for it in items) + 1.0

    # Objective: Minimize M*(diff_plus + diff_minus) - sum(x[i])
    model.obj = Objective(
        expr=M * (model.diff_plus + model.diff_minus)
        - quicksum(model.x[i] for i in model.I)
    )

    # Use Bonmin solver instead of GLPK
    solver = SolverFactory("bonmin")
    solver.solve(model, tee=False)

    chosen = []
    for i in model.I:
        if model.x[i].value >= 0.9999:
            chosen.append(items[i])
    return chosen
