import csv
import os
import sys

from pydantic import ValidationError

from models.combination import Item


def read_items_from_csv(filepath: str) -> list[Item]:
    items = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                item = Item(**row)  # type: ignore
                items.append(item)
            except ValidationError as e:
                sys.stderr.write(f"Invalid row: {row}, error: {e}\n")
    return items


def write_output(filepath: str, chosen_items: list[Item], target_sum: float) -> None:
    # Ensure directory exists
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    total = sum(it.weight for it in chosen_items)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "weight", "sum"])
        for it in chosen_items:
            writer.writerow([it.name, it.weight, total])
