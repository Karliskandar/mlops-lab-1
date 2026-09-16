import logging
import shutil
from pathlib import Path

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Repository root: .../<repo>/src/<pkg>/this_file.py -> parents[2] == <repo>
ROOT = Path(__file__).resolve().parents[2]



RAW_ROOT = ROOT / "data"

OUTPUT_ROOT = ROOT / "local_data"
PROCESSED_ROOT = OUTPUT_ROOT / "food11_processed"
MINI_ROOT = OUTPUT_ROOT / "food11_processed_mini"

print("SCRIPT IS RUNNING")
print("ROOT =", ROOT)
print("RAW_ROOT =", RAW_ROOT if "RAW_ROOT" in globals() else "not defined yet")
SPLITS = ["training", "evaluation", "validation"]

# Food-11 class mapping
CATEGORIES = {
    "0": "Bread",
    "1": "Dairy_product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried_food",
    "5": "Meat",
    "6": "Noodles_Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable_Fruit",
}

IMAGE_SIZE = (128, 128)
IMAGE_GLOB_PATTERN = "*.jpg"
MINI_LIMIT = 100
RESAMPLE_FILTER = Image.Resampling.LANCZOS


def prepare_output_folders() -> None:
    """Remove previously generated output so the script is reproducible."""
    for folder in (PROCESSED_ROOT, MINI_ROOT):
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)


def category_name_for(image_path: Path) -> str | None:
  
    category_id = image_path.stem.split("_")[0]
    return CATEGORIES.get(category_id)


def process_split(split: str) -> None:
    input_folder = RAW_ROOT / split
    if not input_folder.is_dir():
        logger.warning("Split folder not found, skipping: %s", input_folder)
        return

    mini_counts: dict[str, int] = {}
    processed_count = 0
    skipped_count = 0

    for image_path in sorted(input_folder.glob(IMAGE_GLOB_PATTERN)):
        category_name = category_name_for(image_path)
        if category_name is None:
            logger.warning("Skipping unknown category: %s", image_path.name)
            skipped_count += 1
            continue

        processed_category = PROCESSED_ROOT / split / category_name
        mini_category = MINI_ROOT / split / category_name

        try:
            with Image.open(image_path) as image:
                image = image.convert("RGB").resize(IMAGE_SIZE, RESAMPLE_FILTER)
        except OSError as exc:
            logger.warning("Skipping unreadable image %s: %s", image_path.name, exc)
            skipped_count += 1
            continue

        processed_category.mkdir(parents=True, exist_ok=True)
        processed_path = processed_category / image_path.name
        image.save(processed_path)
        processed_count += 1

        count = mini_counts.get(category_name, 0)
        if count < MINI_LIMIT:
            mini_category.mkdir(parents=True, exist_ok=True)
            image.save(mini_category / image_path.name)
            mini_counts[category_name] = count + 1

    logger.info(
        "[%s] processed=%d skipped=%d mini_total=%d",
        split, processed_count, skipped_count, sum(mini_counts.values()),
    )


def process_dataset() -> None:
    for split in SPLITS:
        process_split(split)


def main() -> None:
    prepare_output_folders()
    process_dataset()
    logger.info("Finished.")
    logger.info("Processed dataset: %s", PROCESSED_ROOT)
    logger.info("Mini dataset:      %s", MINI_ROOT)


if __name__ == "__main__":
    main()