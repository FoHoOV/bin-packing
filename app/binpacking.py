from typing import List

from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    Objective,
    SolverFactory,
    SolverStatus,
    TerminationCondition,
    Var,
    quicksum,
)

from models.binpacking import Item


def solve_bin_packing(items: List[Item], capacity: float) -> List[List[Item]]:
    n = len(items)
    model = ConcreteModel()
    model.I = range(n)
    model.B = range(n)

    model.x = Var(model.B, domain=Binary)
    model.y = Var(model.I, model.B, domain=Binary)

    model.obj = Objective(expr=quicksum(model.x[b] for b in model.B))

    def one_bin_per_item_rule(model, i):
        return quicksum(model.y[i, b] for b in model.B) == 1

    model.one_bin_per_item = Constraint(model.I, rule=one_bin_per_item_rule)

    def capacity_rule(model, b):
        return (
            quicksum(items[i].weight * model.y[i, b] for i in model.I)
            <= capacity * model.x[b]
        )

    model.capacity_con = Constraint(model.B, rule=capacity_rule)

    solver = SolverFactory("cbc")
    result = solver.solve(model, tee=True)

    # Check solver status
    if (
        result.solver.termination_condition != TerminationCondition.optimal
        or result.solver.status != SolverStatus.ok
    ):
        # Handle infeasibility or other non-optimal statuses
        # If infeasible, no solution exists under given constraints.
        # You can print a message, raise an exception, or return an empty list.
        print(
            "No feasible solution found. Check if all items fit into a container individually."
        )
        return []  # or raise an exception

    # If here, solution is optimal and feasible
    bins = []
    for b in model.B:
        val = model.x[b].value
        if val is not None and val > 0.9999:
            chosen_items = []
            for i in model.I:
                if model.y[i, b].value is not None and model.y[i, b].value > 0.9999:
                    chosen_items.append(items[i])
            if chosen_items:
                bins.append(chosen_items)

    return bins
