#!/usr/bin/env bash
#
# Creates/reuses a virtual environment, installs the required
# dependencies and runs the learning curve with image selection
# by diversity (least similar pairs via SSIM).
#
# Prerequisite: run ssim_ranking.py first to generate the
# ssim_pares.csv used to order the images.
#
# Usage:
#   ./run_ssim_learning_curve.sh
#   ./run_ssim_learning_curve.sh --ssim-csv /path/ssim_pares.csv
#
set -euo pipefail

# Directory where this script lives (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${SCRIPT_DIR}/.venv"
TRAIN_SCRIPT="${SCRIPT_DIR}/ssim_learning_curve.py"

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
# 4) Run the diversity-based learning curve (SSIM)
#    Forwards any extra arguments (e.g. --ssim-csv)
# ------------------------------------------------------------

echo "==> Starting the diversity-based learning curve (SSIM)"
python "${TRAIN_SCRIPT}" "$@"

echo "==> Done."
