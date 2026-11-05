from pathlib import Path
from collections import Counter

DATASET_DIR = Path("dataset")

IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"
SPLIT_DIR = DATASET_DIR / "split"

CLASS_NAMES = {
    0: "agricultural crops",
    1: "buildings",
    2: "exposed soil",
    3: "pasture",
    4: "vegetation",
}


def read_split(split_name):
    split_file = SPLIT_DIR / f"{split_name}.txt"

    with open(split_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def analyze_split(image_names):
    object_count = Counter()
    image_count = Counter()

    total_objects = 0

    for image_name in image_names:
        image_path = Path(image_name)
        label_path = LABELS_DIR / f"{image_path.stem}.txt"

        classes_in_image = set()

        with open(label_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()

                if not parts:
                    continue

                class_id = int(parts[0])

                object_count[class_id] += 1
                total_objects += 1
                classes_in_image.add(class_id)

        for class_id in classes_in_image:
            image_count[class_id] += 1

    return object_count, image_count, total_objects


print("\n" + "=" * 70)
print("SPLIT DISTRIBUTION")
print("=" * 70)

results = {}

for split in ["train", "val", "test"]:

    images = read_split(split)

    object_count, image_count, total_objects = analyze_split(images)

    results[split] = {
        "images": len(images),
        "objects": total_objects,
        "object_count": object_count,
        "image_count": image_count,
    }

    print(f"\n{'=' * 70}")
    print(f"{split.upper()}")
    print(f"{'=' * 70}")

    print(f"Images:  {len(images)}")
    print(f"Objects: {total_objects}")

    print("\nClass                  Objects    Images")
    print("-" * 50)

    for class_id, class_name in CLASS_NAMES.items():

        print(
            f"{class_name:<22} "
            f"{object_count[class_id]:>7} "
            f"{image_count[class_id]:>9}"
        )


print("\n" + "=" * 70)
print("PERCENTAGE OF OBJECTS PER CLASS")
print("=" * 70)

for split in ["train", "val", "test"]:

    object_count = results[split]["object_count"]
    total = results[split]["objects"]

    print(f"\n{split.upper()}")

    for class_id, class_name in CLASS_NAMES.items():

        percentage = (
            object_count[class_id] / total * 100
            if total > 0
            else 0
        )

        print(
            f"{class_name:<22}: "
            f"{percentage:6.2f}%"
        )