import argparse
import logging

from pipeline import aggregate, build_card, charts, extract, export_portal_json, fetch, inventory
from pipeline.config import DATA_DIR

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    ap = argparse.ArgumentParser(description="Run the full SimReady catalog pipeline")
    ap.add_argument("--limit", type=int, default=None, help="only first N assets (smoke run)")
    ap.add_argument("--skip-fetch", action="store_true", help="skip download stage")
    ap.add_argument("--skip-inventory", action="store_true", help="skip inventory stage")
    args = ap.parse_args()

    if not args.skip_inventory:
        logger.info("== inventory ==")
        inventory.main()
    if not args.skip_fetch:
        logger.info("== fetch ==")
        path = fetch.fetch(limit=args.limit)
        logger.info("snapshot at %s", path)
    logger.info("== extract ==")
    extract.main()
    logger.info("== aggregate ==")
    stats = aggregate.main()
    logger.info("== charts ==")
    charts.main()
    logger.info("== card ==")
    build_card.main()
    logger.info("== portal export ==")
    export_portal_json.main()
    logger.info(
        "done: %d assets, %d categories, as of %s",
        stats["n_assets"], stats["n_categories"], stats["as_of"],
    )


if __name__ == "__main__":
    main()
