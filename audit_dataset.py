from pathlib import Path
from collections import Counter, defaultdict

# =========================
# SETTINGS
# =========================

IMAGES_DIR = Path("dataset/images")
LABELS_DIR = Path("dataset/labels")

CLASS_NAMES = {
    0: "agricultural crops",
    1: "buildings",
    2: "exposed soil",
    3: "pasture",
    4: "vegetation",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# =========================
# FUNCTIONS
# =========================

def get_images():
    return {
        image.stem: image
        for image in IMAGES_DIR.iterdir()
        if image.is_file() and image.suffix.lower() in IMAGE_EXTENSIONS
    }


def get_labels():
    return {
        label.stem: label
        for label in LABELS_DIR.glob("*.txt")
        if label.is_file() and label.name != "classes.txt"
    }


def audit_label(label_path):
    objects = []
    errors = []

    with open(label_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line_number, line in enumerate(lines, start=1):
        parts = line.split()

        if len(parts) != 5:
            errors.append(
                f"Line {line_number}: expected 5 values, found {len(parts)}"
            )
            continue

        try:
            class_id = int(parts[0])
            values = list(map(float, parts[1:]))
        except ValueError:
            errors.append(f"Line {line_number}: invalid values")
            continue

        if class_id not in CLASS_NAMES:
            errors.append(
                f"Line {line_number}: invalid class ({class_id})"
            )
            continue

        x, y, width, height = values

        # YOLO format: values normalized between 0 and 1
        if not all(0 <= value <= 1 for value in values):
            errors.append(
                f"Line {line_number}: coordinates out of [0,1]"
            )

        if width <= 0 or height <= 0:
            errors.append(
                f"Line {line_number}: invalid width/height"
            )

        objects.append(class_id)

    return objects, errors


# =========================
# AUDIT
# =========================

images = get_images()
labels = get_labels()

image_stems = set(images)
label_stems = set(labels)

images_without_labels = sorted(image_stems - label_stems)
labels_without_images = sorted(label_stems - image_stems)

class_object_count = Counter()
class_image_count = Counter()
objects_per_image = Counter()
errors_by_file = defaultdict(list)

total_objects = 0

for stem, label_path in labels.items():

    objects, errors = audit_label(label_path)

    if errors:
        errors_by_file[stem].extend(errors)

    total_objects += len(objects)
    objects_per_image[len(objects)] += 1

    classes_in_image = set(objects)

    for class_id in objects:
        class_object_count[class_id] += 1

    for class_id in classes_in_image:
        class_image_count[class_id] += 1


# =========================
# RESULTS
# =========================

print("\n" + "=" * 60)
print("DATASET AUDIT")
print("=" * 60)

print(f"\nImages found: {len(images)}")
print(f"Labels found: {len(labels)}")
print(f"Total objects: {total_objects}")

print("\n--- MATCHING ---")

print(f"Images without label: {len(images_without_labels)}")
if images_without_labels:
    for name in images_without_labels[:20]:
        print(f"  - {name}")

print(f"\nLabels without image: {len(labels_without_images)}")
if labels_without_images:
    for name in labels_without_images[:20]:
        print(f"  - {name}")


print("\n--- CLASSES ---")

for class_id, class_name in CLASS_NAMES.items():
    print(
        f"{class_id}: {class_name:<20} "
        f"objects={class_object_count[class_id]:>6} | "
        f"images={class_image_count[class_id]:>6}"
    )


print("\n--- OBJECTS PER IMAGE ---")

for num_objects in sorted(objects_per_image):
    print(
        f"{num_objects:>3} object(s): "
        f"{objects_per_image[num_objects]} image(s)"
    )


print("\n--- LABEL ERRORS ---")

if not errors_by_file:
    print("No errors found.")
else:
    print(f"Files with errors: {len(errors_by_file)}")

    for stem, errors in list(errors_by_file.items())[:20]:
        print(f"\n{stem}:")
        for error in errors:
            print(f"  - {error}")


print("\n" + "=" * 60)
print("END OF AUDIT")
print("=" * 60)
