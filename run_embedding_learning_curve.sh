#!/usr/bin/env bash
#
# Creates/reuses a virtual environment, installs the required
# dependencies and runs the learning curve with image selection
# by diversity (least similar pairs via cosine of embeddings).
#
# Prerequisite: run embedding_ranking.py first to generate the
# embedding_pares.csv used to order the images.
#
# Usage:
#   ./run_embedding_learning_curve.sh
#   ./run_embedding_learning_curve.sh --embedding-csv /path/embedding_pares.csv
#
set -euo pipefail

# Directory where this script lives (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${SCRIPT_DIR}/.venv"
TRAIN_SCRIPT="${SCRIPT_DIR}/embedding_learning_curve.py"

# ------------------------------------------------------------
# 1) Create the virtual environment (only if it doesn't exist)
# ------------------------------------------------------------

if [ ! -d "${VENV_DIR}" ]; then
    echo "==> Creating virtual environment at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
else
    echo "==> Reusing existing virtual environment at ${VENV_DIR}"
fi

# ------------------------------------------------------------
# 2) Activate the venv
# ------------------------------------------------------------

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# ------------------------------------------------------------
# 3) Install/upgrade dependencies
# ------------------------------------------------------------

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing dependencies (ultralytics, matplotlib, pyyaml)"
python -m pip install --upgrade ultralytics matplotlib pyyaml

# ------------------------------------------------------------
# 4) Run the diversity-based learning curve (embeddings)
#    Forwards any extra arguments (e.g. --embedding-csv)
# ------------------------------------------------------------

echo "==> Starting the diversity-based learning curve (DINOv2 embeddings)"
python "${TRAIN_SCRIPT}" "$@"

echo "==> Done."
