#!/usr/bin/env bash
#
# Creates/reuses a virtual environment, installs the required
# dependencies and runs the YOLO models learning curve script
# (incremental training, 10 images at a time).
#
# Usage:
#   ./run_train_learning_curve.sh
#
set -euo pipefail

# Directory where this script lives (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${SCRIPT_DIR}/.venv"
TRAIN_SCRIPT="${SCRIPT_DIR}/train_learning_curve.py"

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
# ultralytics already brings torch, opencv, numpy, etc. as dependencies
# pyyaml is used to read/write the subsets' data.yaml files
python -m pip install --upgrade ultralytics matplotlib pyyaml

# ------------------------------------------------------------
# 4) Run the learning curve
# ------------------------------------------------------------

echo "==> Starting the models learning curve"
python "${TRAIN_SCRIPT}"

echo "==> Done."
