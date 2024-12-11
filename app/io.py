import csv
import os
import sys
from typing import List

from pydantic import ValidationError

from models.binpacking import Item


def read_items_from_csv(filepath: str) -> List[Item]:
    items = []
    print("reading file")
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                item = Item(**row)  # type: ignore
                items.append(item)
            except ValidationError as e:
                sys.stderr.write(f"Invalid row: {row}, error: {e}\n")
    print("done")
    return items


def write_output(filepath: str, bins: List[List[Item]], capacity: float) -> None:
    print("writing result")
    # Ensure output directory exists
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["container_id", "name", "weight", "sum"])
        for b_idx, bin_items in enumerate(bins):
            total = sum(it.weight for it in bin_items)
            for it in bin_items:
                writer.writerow([b_idx, it.name, it.weight, total])
