import argparse
from models.cli import Cli


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    parser.add_argument("--sum", required=True, type=float, help="Target sum")
    args = parser.parse_args()
    return Cli(sum=args.sum, input=args.input, output=args.output)
