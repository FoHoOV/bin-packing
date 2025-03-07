from app.binpacking import solve_bin_packing
from app.models.binpacking import Item


def test_binpacking_small():
    items = [
        Item(name="item1", weight=14),
        Item(name="item2", weight=15),
        Item(name="item3", weight=27),
        Item(name="item4", weight=4),
        Item(name="item5", weight=60),
    ]
    capacity = 60
    bins = solve_bin_packing(items, capacity)

    # Check all items are included once
    chosen_items = [item.name for bin in bins for item in bin]
    assert set(chosen_items) == {it.name for it in items}

    # Check capacity constraints
    for bin in bins:
        assert sum(i.weight for i in bin) <= capacity

    # Known optimal solution is 2 bins for this problem
    assert len(bins) == 2
