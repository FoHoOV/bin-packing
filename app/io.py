import csv
import os
import sys
from io import StringIO

import pandas
from pydantic import ValidationError

from models.binpacking import Item


def read_items_from_csv(filepath: str) -> list[Item]:
    items = []
    print("reading file")

    if not filepath.endswith(".csv"):
        raise ValidationError("only csv files are allowed")

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


def _write_csv(filepath: str, buffer: StringIO):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        f.writelines(buffer.readlines())


def _write_table(filepath: str, buffer: StringIO):
    pandas.read_csv(buffer).to_markdown(
        os.path.join(
            os.path.dirname(filepath), f"{os.path.basename(filepath)}-pretty.csv"
        ),
        index=False,
    )


def write_output(filepath: str, bins: list[list[Item]], capacity: int) -> None:
    print("writing result")

    if not filepath.endswith(".csv"):
        raise ValidationError("only csv files are allowed")

    # Ensure output directory exists
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    buffer = create_buffer(bins, capacity)

    buffer.seek(0)
    _write_csv(filepath, buffer)

    buffer.seek(0)
    _write_table(filepath, buffer)


def create_buffer(bins: list[list[Item]], capacity: int):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["container_id", "name", "weight", "sum"])
    total = 0
    for bin_index, bin_items in enumerate(bins):
        total_per_pack = sum(item.weight for item in bin_items)
        total += total_per_pack
        for item in bin_items:
            writer.writerow(
                [bin_index + 1, item.name, item.weight, f"{total_per_pack:,}"]
            )
    writer.writerow(["-", "-", f"{total:,}", f"{total:,}"])
    return buffer
