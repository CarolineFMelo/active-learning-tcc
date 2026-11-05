#!/usr/bin/env bash
#
# Creates/reuses a virtual environment, installs the required
# dependencies and runs the YOLO models comparison script.
#
# Usage:
#   ./run_train_compare.sh
#
set -euo pipefail

# Directory where this script lives (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${SCRIPT_DIR}/.venv"
TRAIN_SCRIPT="${SCRIPT_DIR}/train_compare.py"

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

echo "==> Installing dependencies (ultralytics, matplotlib)"
# ultralytics already brings torch, opencv, numpy, etc. as dependencies
python -m pip install --upgrade ultralytics matplotlib

# ------------------------------------------------------------
# 4) Run the training/comparison
# ------------------------------------------------------------

echo "==> Starting the models training and comparison"
python "${TRAIN_SCRIPT}"

echo "==> Done."
