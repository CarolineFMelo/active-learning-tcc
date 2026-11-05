from pathlib import Path
from collections import defaultdict
import random

# =========================
# SETTINGS
# =========================

DATASET_DIR = Path("dataset")
IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"

SPLIT_DIR = DATASET_DIR / "split"

SEED = 42

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

CLASS_IDS = {0, 1, 2, 3, 4}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}


# =========================
# FUNCTIONS
# =========================

def get_images():
    return sorted(
        [
            image
            for image in IMAGES_DIR.iterdir()
            if image.is_file()
            and image.suffix.lower() in IMAGE_EXTENSIONS
        ]
    )


def get_classes_from_label(label_path):
    classes = set()

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if not parts:
                continue

            class_id = int(parts[0])

            if class_id in CLASS_IDS:
                classes.add(class_id)

    return classes


# =========================
# LOAD IMAGES
# =========================

images = get_images()

if len(images) != 700:
    print(f"Warning: found {len(images)} images.")


# =========================
# GROUP BY CLASSES
# =========================

class_to_images = defaultdict(list)

for image in images:
    label_path = LABELS_DIR / f"{image.stem}.txt"

    if not label_path.exists():
        raise FileNotFoundError(
            f"Label not found for: {image.name}"
        )

    classes = get_classes_from_label(label_path)

    for class_id in classes:
        class_to_images[class_id].append(image)


# =========================
# STRATIFIED SELECTION
# =========================

random.seed(SEED)

selected = {
    "train": set(),
    "val": set(),
    "test": set(),
}

# Distribute images per class.
# Images with multiple classes may temporarily appear in more than one list.
# Then resolve conflicts by prioritizing the split that still needs that class the most.

remaining = set(images)

# Order: rarest classes first
class_order = sorted(
    CLASS_IDS,
    key=lambda c: len(class_to_images[c])
)

for class_id in class_order:

    candidates = class_to_images[class_id].copy()
    random.shuffle(candidates)

    # Consider only images not yet distributed
    candidates = [
        image
        for image in candidates
        if image in remaining
    ]

    n = len(candidates)

    n_test = round(n * TEST_RATIO)
    n_val = round(n * VAL_RATIO)

    test_images = candidates[:n_test]
    val_images = candidates[n_test:n_test + n_val]
    train_images = candidates[n_test + n_val:]

    for image in test_images:
        selected["test"].add(image)

    for image in val_images:
        selected["val"].add(image)

    for image in train_images:
        selected["train"].add(image)

    remaining -= set(candidates)


# =========================
# DISTRIBUTE REMAINING IMAGES
# =========================

remaining = list(remaining)
random.shuffle(remaining)

target_train = round(len(images) * TRAIN_RATIO)
target_val = round(len(images) * VAL_RATIO)
target_test = len(images) - target_train - target_val

for image in remaining:

    sizes = {
        "train": len(selected["train"]),
        "val": len(selected["val"]),
        "test": len(selected["test"]),
    }

    targets = {
        "train": target_train,
        "val": target_val,
        "test": target_test,
    }

    available = [
        split
        for split in sizes
        if sizes[split] < targets[split]
    ]

    if not available:
        break

    split = max(
        available,
        key=lambda s: targets[s] - sizes[s]
    )

    selected[split].add(image)


# =========================
# FINAL CHECK
# =========================

all_selected = (
    selected["train"]
    | selected["val"]
    | selected["test"]
)

missing = set(images) - all_selected
duplicates = (
    (selected["train"] & selected["val"])
    | (selected["train"] & selected["test"])
    | (selected["val"] & selected["test"])
)

if missing:
    raise RuntimeError(
        f"Images not distributed: {len(missing)}"
    )

if duplicates:
    raise RuntimeError(
        f"Images duplicated across splits: {len(duplicates)}"
    )


# =========================
# SAVE
# =========================

SPLIT_DIR.mkdir(parents=True, exist_ok=True)

for split, split_images in selected.items():

    output_file = SPLIT_DIR / f"{split}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        for image in sorted(split_images):
            f.write(f"{image.name}\n")


# =========================
# RESULT
# =========================

print("\n" + "=" * 50)
print("DATASET SPLIT")
print("=" * 50)

print(f"\nSeed: {SEED}")

print(f"\nTrain: {len(selected['train'])}")
print(f"Val:   {len(selected['val'])}")
print(f"Test:  {len(selected['test'])}")

print(f"\nTotal: {len(all_selected)}")

print("\nFiles created:")

for split in ["train", "val", "test"]:
    print(
        f"  {SPLIT_DIR / f'{split}.txt'}"
    )

print("\n" + "=" * 50)