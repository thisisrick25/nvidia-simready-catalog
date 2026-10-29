import argparse

from pipeline import aggregate, build_card, charts, extract, fetch, inventory


def main():
    ap = argparse.ArgumentParser(description="Run the full SimReady catalog pipeline")
    ap.add_argument("--limit", type=int, default=None, help="only first N assets (smoke run)")
    ap.add_argument("--skip-fetch", action="store_true", help="skip download stage")
    ap.add_argument("--skip-inventory", action="store_true", help="skip inventory stage")
    args = ap.parse_args()

    if not args.skip_inventory:
        print("== inventory ==")
        inventory.main()
    if not args.skip_fetch:
        print("== fetch ==")
        path = fetch.fetch(limit=args.limit)
        print(f"snapshot at {path}")
    print("== extract ==")
    extract.main()
    print("== aggregate ==")
    stats = aggregate.main()
    print("== charts ==")
    charts.main()
    print("== card ==")
    build_card.main()
    print(f"done: {stats['n_assets']} assets, {stats['n_categories']} categories, as of {stats['as_of']}")


if __name__ == "__main__":
    main()