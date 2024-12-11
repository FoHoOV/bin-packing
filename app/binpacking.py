from typing import cast

from pyomo.environ import Binary  # type: ignore
from pyomo.environ import (
    ConcreteModel,
    Constraint,
    Objective,
    SolverFactory,
    SolverStatus,
    TerminationCondition,
    Var,
    quicksum,
    value,
)

from models.binpacking import Item


def solve_bin_packing(items: list[Item], capacity: float):
    # Sort items by descending weight to help MIP performance slightly
    sorted_items = sorted(items, key=lambda x: x.weight, reverse=True)
    num_items = len(sorted_items)

    # Check feasibility: if any single item exceeds capacity, no solution is possible
    for item in sorted_items:
        if item.weight > capacity:
            raise ValueError("Item heavier than capacity, infeasible.")

    # Use a heuristic (First-Fit Decreasing) to find an initial upper bound on the number of bins
    heuristic_solution = first_fit_decreasing(sorted_items, capacity)
    num_bins = len(heuristic_solution)  # upper bound on number of bins needed

    # Build the MIP model
    model = ConcreteModel()
    model.ITEMS = range(num_items)
    model.BINS = range(num_bins)

    # bin_used[bin_index] = 1 if bin is used, 0 otherwise
    # item_in_bin[item_index, bin_index] = 1 if item is placed in that bin, 0 otherwise
    model.bin_used = Var(model.BINS, domain=Binary)
    model.item_in_bin = Var(model.ITEMS, model.BINS, domain=Binary)

    # Objective: minimize the number of bins used
    model.obj = Objective(
        expr=quicksum(model.bin_used[bin_index] for bin_index in model.BINS)
    )

    # Each item must be placed in exactly one bin
    def one_bin_per_item_rule(model, item_index):
        return (
            quicksum(
                model.item_in_bin[item_index, bin_index] for bin_index in model.BINS
            )
            == 1
        )

    model.one_bin_per_item_con = Constraint(model.ITEMS, rule=one_bin_per_item_rule)

    # Capacity constraint: total weight in a bin must not exceed capacity if bin is used
    def capacity_rule(model, bin_index):
        return (
            quicksum(
                sorted_items[item_index].weight
                * model.item_in_bin[item_index, bin_index]
                for item_index in model.ITEMS
            )
            <= capacity * model.bin_used[bin_index]
        )

    model.capacity_con = Constraint(model.BINS, rule=capacity_rule)

    # Symmetry breaking: ensure non-increasing usage of bins to avoid symmetric solutions
    # If bin b is used (x[b]=1), then all bins < b must also be used.
    def symmetry_break_rule(model, bin_index):
        if bin_index == 0:
            return Constraint.Skip
        return model.bin_used[bin_index - 1] >= model.bin_used[bin_index]

    model.symmetry_con = Constraint(model.BINS, rule=symmetry_break_rule)

    # MIP Start: provide a good initial solution from the heuristic
    item_name_to_index = {item.name: idx for idx, item in enumerate(sorted_items)}
    for bin_index, bin_items_list in enumerate(heuristic_solution):
        model.bin_used[bin_index].set_value(1)  # type: ignore
        for item in bin_items_list:
            i = item_name_to_index[item.name]
            model.item_in_bin[i, bin_index].set_value(1)  # type: ignore
    # For any unused bins (if any), set x to 0
    for bin_index in range(len(heuristic_solution), num_bins):
        model.bin_used[bin_index].set_value(0)  # type: ignore

    solver = SolverFactory("cbc")
    # Optional solver parameters can be set here
    # solver.options['ratio'] = 0.01  # e.g., set MIP gap tolerance
    # solver.options['seconds'] = 60  # e.g., set time limit

    result = solver.solve(model, tee=True)

    # Check solver status
    if (
        result.solver.termination_condition != TerminationCondition.optimal
        or result.solver.status != SolverStatus.ok
    ):
        raise ValueError(f"No optimal solution found. Status: {result.solver.status}")

    # Extract the final solution
    final_bins: list[list[Item]] = []
    for bin_index in model.BINS:
        if cast(int, value(model.bin_used[bin_index])) > 0.9999:
            selected_items: list[Item] = []
            for item_index in model.ITEMS:
                if cast(int, value(model.item_in_bin[item_index, bin_index])) > 0.9999:
                    selected_items.append(sorted_items[item_index])
            if selected_items:
                final_bins.append(selected_items)

    check_output(items, final_bins)
    return final_bins


def first_fit_decreasing(sorted_items: list[Item], capacity: float) -> list[list[Item]]:
    """Heuristic to find an initial bin assignment:
    Sort items in descending order (already sorted), then
    place each item into the first bin it fits into, or create a new bin if none fit."""
    bins = []
    for item in sorted_items:
        placed = False
        for bin_contents in bins:
            if sum(i.weight for i in bin_contents) + item.weight <= capacity:
                bin_contents.append(item)
                placed = True
                break
        if not placed:
            bins.append([item])
    return bins


def check_output(input: list[Item], output: list[list[Item]]):
    used: dict[str, bool] = {}

    for bin in output:
        for item in bin:
            found = next(
                filter(
                    lambda found: found.name == item.name
                    and found.weight == item.weight,
                    input,
                ),
                None,
            )
            if found is None or used.get(item.name, None) is not None:
                raise Exception("invalid output generated! it's a bug :(")
            used[item.name] = True

    if len(used.keys()) != len(input):
        raise Exception(
            "invalid output generated! it's a bug (all items are not used) :("
        )
