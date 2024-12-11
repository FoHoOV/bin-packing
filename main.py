from app.binpacking import solve_bin_packing
from app.cli import cli
from app.io import read_items_from_csv, write_output


def main():
    args = cli()
    items = read_items_from_csv(args.input)
    result = solve_bin_packing(items, args.sum)
    write_output(args.output, result, args.sum)


if __name__ == "__main__":
    main()
