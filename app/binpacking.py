from typing import List

from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Objective,
    SolverFactory,
    SolverStatus,
    TerminationCondition,
    Var,
    quicksum,
)

from models.binpacking import Item


def solve_bin_packing(items: List[Item], capacity: float) -> List[List[Item]]:
    # Sort items by descending weight to improve MIP performance slightly
    sorted_items = sorted(items, key=lambda x: x.weight, reverse=True)
    n = len(sorted_items)

    # Check if any item is heavier than capacity (infeasible)
    for it in sorted_items:
        if it.weight > capacity:
            print("Item heavier than capacity, infeasible.")
            return []

    # Use a heuristic to find an initial upper bound on bins
    heuristic_bins = first_fit_decreasing(sorted_items, capacity)
    H = len(heuristic_bins)  # upper bound on number of bins

    # Build MIP model with H bins instead of n
    model = ConcreteModel()
    model.I = range(n)
    model.B = range(H)

    model.x = Var(model.B, domain=Binary)
    model.y = Var(model.I, model.B, domain=Binary)

    model.obj = Objective(expr=quicksum(model.x[b] for b in model.B))

    def one_bin_per_item_rule(m, i):
        return quicksum(m.y[i, b] for b in m.B) == 1

    model.one_bin_per_item = Constraint(model.I, rule=one_bin_per_item_rule)

    def capacity_rule(m, b):
        return (
            quicksum(sorted_items[i].weight * m.y[i, b] for i in m.I)
            <= capacity * m.x[b]
        )

    model.capacity_con = Constraint(model.B, rule=capacity_rule)

    # Symmetry breaking: ensure that bin usage is non-increasing
    # if bin b is used (x[b]=1), then all bins < b must be used.
    # x[0] >= x[1] >= x[2] ... This removes symmetric solutions.
    def symmetry_break_rule(m, b):
        if b == 0:
            return Constraint.Skip
        return m.x[b - 1] >= m.x[b]

    model.symmetry_con = Constraint(model.B, rule=symmetry_break_rule)

    # MIP Start (optional): Assign heuristic solution to model.y and model.x
    # Note: This is a hint to the solver. Some solvers support it directly,
    # for CBC this might not always yield improvements, but we try anyway.
    # Map the heuristic solution (heuristic_bins) back to the indexes in sorted_items
    item_index_map = {it.name: i for i, it in enumerate(sorted_items)}
    for b_idx, bin_ in enumerate(heuristic_bins):
        model.x[b_idx].value = 1
        for it in bin_:
            i = item_index_map[it.name]
            model.y[i, b_idx].value = 1
    # For any unused bin in heuristic, set x[b].value = 0
    for b_idx in range(len(heuristic_bins), H):
        model.x[b_idx].value = 0

    solver = SolverFactory("cbc")
    # Optionally set solver parameters if desired (depends on CBC version):
    # solver.options['ratio'] = 0.01  # for example, MIP gap tolerance
    # solver.options['seconds'] = 60  # time limit
    # ... Add more if needed.

    result = solver.solve(model, tee=True)

    # Check solver status
    if (
        result.solver.termination_condition != TerminationCondition.optimal
        or result.solver.status != SolverStatus.ok
    ):
        print("No optimal solution found. Status:", result.solver.status)
        return []

    # Extract solution
    bins = []
    for b in model.B:
        if model.x[b].value > 0.9999:
            chosen_items = []
            for i in model.I:
                if model.y[i, b].value > 0.9999:
                    chosen_items.append(sorted_items[i])
            if chosen_items:
                bins.append(chosen_items)

    return bins


def first_fit_decreasing(items: List[Item], capacity: float) -> List[List[Item]]:
    sorted_items = sorted(items, key=lambda x: x.weight, reverse=True)
    bins = []
    for it in sorted_items:
        placed = False
        for bin_ in bins:
            if sum(i.weight for i in bin_) + it.weight <= capacity:
                bin_.append(it)
                placed = True
                break
        if not placed:
            bins.append([it])
    return bins
