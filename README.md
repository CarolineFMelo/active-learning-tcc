# TCC Scripts — YOLO Training & Sampling Experiments

Scripts for the thesis experiments on object detection in aerial/satellite
imagery, comparing three recent YOLO versions (YOLOv8s, YOLO11s, YOLO26s) under
different **data sampling strategies**.

The dataset has 5 classes: `agricultural crops`, `buildings`, `exposed soil`,
`pasture`, `vegetation`.

---

## Overview

The repository is organized around two ideas:

1. **Model comparison** — train the three YOLO versions on the full dataset and
   compare them.
2. **Sampling strategies** — study how the *way* training images are selected
   affects performance, through a learning curve that grows the training set 10
   images at a time (cumulative) until it reaches 100% of the data. Validation
   and test sets stay fixed so the curves are comparable.

Three sampling strategies are implemented, all sharing the same models,
hyperparameters and evaluation protocol — only the image selection differs:

| Strategy | Criterion | Ranking script | Learning curve script |
|---|---|---|---|
| Random (baseline) | shuffle with fixed seed | — | `train_learning_curve.py` |
| SSIM | pixel-level structural similarity | `ssim_ranking.py` | `ssim_learning_curve.py` |
| Embeddings (DINOv2) | semantic cosine similarity | `embedding_ranking.py` | `embedding_learning_curve.py` |

The SSIM and embedding strategies select images by **least similar pairs**
(diversity): they build a ranking of all image pairs and add the two images of
each pair, from least to most similar, skipping pairs whose images were already
added.

---

## Requirements

- Python 3.10+
- A GPU is strongly recommended for the training scripts (`DEVICE = 0`). Set
  `DEVICE = "cpu"` in the script if you have no GPU.
- Internet on first run (model weights and DINOv2 are downloaded automatically).

Each `run_*.sh` creates/reuses a local virtual environment at `scripts/.venv`
and installs the dependencies it needs, so you don't have to manage them by
hand.

---

## Execution order

### 1. Dataset preparation

```bash
# 1. (optional) audit labels and image/label matching
python3 audit_dataset.py

# 2. create the stratified train/val/test splits (seed = 42)
python3 create_splits.py

# 3. (optional) inspect the class distribution per split
python3 check_splits.py

# 4. build the YOLO dataset folder + data.yaml
python3 prepare_yolo_dataset.py
```

After step 4 you get `dataset_yolo/` with `images/{train,val,test}`,
`labels/{train,val,test}` and `data.yaml`. All experiment scripts read this
`data.yaml`.

### 2. Model comparison (full dataset)

```bash
./run_train_compare.sh
```

### 3. Learning curves (sampling strategies)

Random baseline (no ranking needed):

```bash
./run_train_learning_curve.sh
```

SSIM — first build the pair ranking, then run the curve:

```bash
./run_ssim_ranking.sh
./run_ssim_learning_curve.sh            # uses the most recent ranking CSV
# or point to a specific CSV:
./run_ssim_learning_curve.sh --ssim-csv /path/to/ssim_pares.csv
```

Embeddings (DINOv2) — same two-step flow:

```bash
./run_embedding_ranking.sh
./run_embedding_learning_curve.sh       # uses the most recent ranking CSV
# or:
./run_embedding_learning_curve.sh --embedding-csv /path/to/embedding_pares.csv
```

The learning curve scripts automatically pick the most recent ranking CSV from
the corresponding `runs_*` folder, so running the ranking before the curve is
enough.

---

## Scripts

### Dataset utilities

- **`audit_dataset.py`** — audits labels (YOLO format, class ids, normalized
  coordinates) and checks image/label matching. Reports per-class counts and
  label errors.
- **`create_splits.py`** — builds stratified `train.txt` / `val.txt` /
  `test.txt` (80/10/10) with a fixed seed, prioritizing rare classes.
- **`check_splits.py`** — prints object and image counts per class for each
  split, plus the percentage of objects per class.
- **`prepare_yolo_dataset.py`** — copies images/labels into the YOLO folder
  structure and writes `data.yaml`.

### Experiments

- **`train_compare.py`** — trains the 3 models on the full dataset and compares
  them (table + bar charts).
- **`train_learning_curve.py`** — learning curve with **random** selection
  (baseline).
- **`ssim_ranking.py`** — computes SSIM for all training-image pairs and saves
  the ranking (`ssim_pares.csv`).
- **`ssim_learning_curve.py`** — learning curve with **SSIM diversity**
  selection, consuming the SSIM ranking.
- **`embedding_ranking.py`** — extracts DINOv2 embeddings for all training
  images, computes pairwise cosine similarity and saves the ranking
  (`embedding_pares.csv`); also saves `embeddings.npy`.
- **`embedding_learning_curve.py`** — learning curve with **embedding
  diversity** selection, consuming the embedding ranking.

### Runners

Each experiment script has a matching `run_*.sh` that sets up the virtualenv,
installs dependencies and runs it:
`run_train_compare.sh`, `run_train_learning_curve.sh`, `run_ssim_ranking.sh`,
`run_ssim_learning_curve.sh`, `run_embedding_ranking.sh`,
`run_embedding_learning_curve.sh`.

---

## Shared configuration

All experiment scripts share the same setup (edit the constants at the top of
each file if needed):

| Parameter | Value |
|---|---|
| Models | `yolov8s`, `yolo11s`, `yolo26s` |
| Epochs (max) | 300 |
| Image size | 640 x 640 |
| Batch | 16 |
| Early stopping (patience) | 20 |
| Seed | 42 |
| Device | 0 (first GPU) |
| Curve step | 10 images |

The **small (s)** variant was chosen because, on small/imbalanced datasets,
increasing model capacity does not consistently improve accuracy and raises the
overfitting risk. The **test** set is used for the reported metrics (mAP50,
mAP50-95, precision, recall) and the **val** set is used for early stopping —
both fixed across all runs.

---

## Outputs

Each experiment writes to its own `runs_*` folder under the project root, with a
timestamped subfolder per run:

| Script | Output folder |
|---|---|
| `train_compare.py` | `runs_comparacao/` |
| `train_learning_curve.py` | `runs_curva_random/` |
| `ssim_ranking.py` | `runs_ssim/` |
| `ssim_learning_curve.py` | `runs_curva_ssim/` |
| `embedding_ranking.py` | `runs_embedding/` |
| `embedding_learning_curve.py` | `runs_curva_embedding/` |

Typical artifacts per run: `metricas.csv`, `metricas.md`, the learning-curve /
comparison charts (`.png`), the per-model training runs (weights, logs), and —
for the ranking scripts — the pairs CSV and ranking markdown.

> Note: the ranking CSVs use the columns `image_a`, `image_b` and the score
> column (`ssim` or `cosine`). If you regenerate a ranking, the matching
> learning curve reads these columns directly.
