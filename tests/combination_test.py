import pytest


from app.combination import solve_knapsack
from models.combination import Item


def test_solve_knapsack_direct():
    # Setup the same scenario used before:
    # inventory:
    # name,weight
    # item1,14
    # item2,15
    # item3,27
    # item4,4
    # item5,60
    items = [
        Item(name="item1", weight=14),
        Item(name="item2", weight=15),
        Item(name="item3", weight=27),
        Item(name="item4", weight=4),
        Item(name="item5", weight=60),
    ]
    target_sum = 62

    chosen = solve_knapsack(items, target_sum)
    chosen_names = {it.name for it in chosen}
    total_weight = sum(it.weight for it in chosen)

    # Check that we have the expected combination
    assert chosen_names == {"item1", "item2", "item3", "item4"}
    # Their total weight is 60, which is closest to 62 with the most items.
    assert abs(total_weight - 60) < 1e-9
