from pathlib import Path
import shutil

# ============================================================
# SETTINGS
# ============================================================

SOURCE = Path(
    "dataset"
)

OUTPUT = Path(
    "dataset_yolo"
)

CLASS_NAMES = {
    0: "agricultural crops",
    1: "buildings",
    2: "exposed soil",
    3: "pasture",
    4: "vegetation",
}


# ============================================================
# CREATE STRUCTURE
# ============================================================

for split in ["train", "val", "test"]:

    (OUTPUT / "images" / split).mkdir(
        parents=True,
        exist_ok=True
    )

    (OUTPUT / "labels" / split).mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# COPY FILES
# ============================================================

total_images = 0
total_labels = 0

for split in ["train", "val", "test"]:

    split_file = SOURCE / "split" / f"{split}.txt"

    if not split_file.exists():
        raise FileNotFoundError(
            f"Split not found: {split_file}"
        )

    with open(split_file, "r", encoding="utf-8") as f:
        image_names = [
            line.strip()
            for line in f
            if line.strip()
        ]

    for image_name in image_names:

        image_src = SOURCE / "images" / image_name
        label_src = SOURCE / "labels" / (
            Path(image_name).stem + ".txt"
        )

        if not image_src.exists():
            raise FileNotFoundError(
                f"Image not found: {image_src}"
            )

        if not label_src.exists():
            raise FileNotFoundError(
                f"Label not found: {label_src}"
            )

        image_dst = (
            OUTPUT / "images" / split / image_name
        )

        label_dst = (
            OUTPUT / "labels" / split /
            f"{Path(image_name).stem}.txt"
        )

        shutil.copy2(image_src, image_dst)
        shutil.copy2(label_src, label_dst)

        total_images += 1
        total_labels += 1

    print(
        f"{split.upper():5} -> "
        f"{len(image_names):3} images"
    )


# ============================================================
# CREATE DATA.YAML
# ============================================================

yaml_lines = [
    f"path: {OUTPUT}",
    "",
    "train: images/train",
    "val: images/val",
    "test: images/test",
    "",
    "names:",
]

for class_id, class_name in CLASS_NAMES.items():
    yaml_lines.append(
        f"  {class_id}: {class_name}"
    )

yaml_path = OUTPUT / "data.yaml"

with open(yaml_path, "w", encoding="utf-8") as f:
    f.write("\n".join(yaml_lines) + "\n")


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)
print("YOLO DATASET PREPARED")
print("=" * 60)

print(f"\nSource:")
print(SOURCE)

print(f"\nDestination:")
print(OUTPUT)

print(f"\nImages copied: {total_images}")
print(f"Labels copied: {total_labels}")

print("\ndata.yaml:")
print("-" * 60)
print(yaml_path.read_text())

print("=" * 60)
