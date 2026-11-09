import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

SPLITS = ["training", "validation", "evaluation"]

EXPECTED_CLASSES = {
    "Bread",
    "Dairy_product",
    "Dessert",
    "Egg",
    "Fried_food",
    "Meat",
    "Noodles_Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable_Fruit",
}


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def validate_dataset(
    dataset_root: Path,
    min_per_class: int,
    tau: float,
) -> bool:
    results: list[tuple[str, bool, str]] = []

    # 1. Check that every split contains exactly the 11 class folders
    folders_ok = True

    for split in SPLITS:
        split_path = dataset_root / split

        if not split_path.is_dir():
            folders_ok = False
            continue

        actual_classes = {
            path.name
            for path in split_path.iterdir()
            if path.is_dir()
        }

        if actual_classes != EXPECTED_CLASSES:
            folders_ok = False

    results.append(
        (
            "11 class folders in every split",
            folders_ok,
            "",
        )
    )

    # 2. Check image validity, mode and size
    images_ok = True

    for split in SPLITS:
        split_path = dataset_root / split

        if not split_path.exists():
            continue

        for image_path in split_path.rglob("*.jpg"):
            try:
                with Image.open(image_path) as image:
                    image.load()

                    if image.mode != "RGB":
                        images_ok = False

                    if image.size != (128, 128):
                        images_ok = False

            except (UnidentifiedImageError, OSError):
                images_ok = False

    results.append(
        (
            "All images are valid RGB 128x128",
            images_ok,
            "",
        )
    )

    # 3. Minimum number of images per class
    minimum_ok = True

    for split in SPLITS:
        for class_name in EXPECTED_CLASSES:
            class_path = dataset_root / split / class_name

            if not class_path.exists():
                minimum_ok = False
                continue

            count = len(list(class_path.glob("*.jpg")))

            if count < min_per_class:
                minimum_ok = False

    results.append(
        (
            f"At least {min_per_class} images per class",
            minimum_ok,
            "",
        )
    )

    # 4. No identical image may appear in different splits
    duplicates_ok = True
    seen_hashes: dict[str, str] = {}

    for split in SPLITS:
        split_path = dataset_root / split

        if not split_path.exists():
            continue

        for image_path in split_path.rglob("*.jpg"):
            digest = md5(image_path)

            if digest in seen_hashes and seen_hashes[digest] != split:
                duplicates_ok = False
            else:
                seen_hashes[digest] = split

    results.append(
        (
            "No image appears in multiple splits",
            duplicates_ok,
            "",
        )
    )

    # 5. Compare class proportions in training and validation
    proportions_ok = True

    training_root = dataset_root / "training"
    validation_root = dataset_root / "validation"

    training_counts = {}
    validation_counts = {}

    for class_name in EXPECTED_CLASSES:
        training_counts[class_name] = len(
            list((training_root / class_name).glob("*.jpg"))
        )
        validation_counts[class_name] = len(
            list((validation_root / class_name).glob("*.jpg"))
        )

    total_training = sum(training_counts.values())
    total_validation = sum(validation_counts.values())

    if total_training == 0 or total_validation == 0:
        proportions_ok = False
    else:
        for class_name in EXPECTED_CLASSES:
            training_share = (
                training_counts[class_name] / total_training
            )
            validation_share = (
                validation_counts[class_name] / total_validation
            )

            if abs(training_share - validation_share) > tau:
                proportions_ok = False

    results.append(
        (
            f"Training/validation class shares within tau={tau}",
            proportions_ok,
            "",
        )
    )

    print("\nDataset validation report")

    for name, passed, _ in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {name}")

    return all(passed for _, passed, _ in results)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "dataset",
        type=Path,
    )

    parser.add_argument(
        "--min-per-class",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--tau",
        type=float,
        default=0.05,
    )

    args = parser.parse_args()

    success = validate_dataset(
        args.dataset,
        args.min_per_class,
        args.tau,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()