#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translate a sentence using OpenNMT-py CLI and a trained model,
then detokenize BPE/subword output entirely in Python.
Fully cross-platform (no Bash required).
"""

import subprocess
import tempfile
import sys
import os

# --------- Configuration ---------
MODEL_PATH = "model_step_20000.pt"   # your trained model
CONFIG_PATH = "config_trans.yaml"    # your YAML config
OUTPUT_FILE = "pred.txt"             # OpenNMT default output

# --------- Utility Functions ---------
def detokenize_bpe(text: str) -> str:
    """Merge BPE/subword tokens (remove @@ markers)."""
    return text.replace("@@ ", "").replace("@@", "")

# --------- Translation Function ---------
def translate_cli(sentence: str) -> str:
    """Translate a single sentence and detokenize BPE output."""
    # --- Step 1: write sentence to temporary file for OpenNMT ---
    with tempfile.NamedTemporaryFile("w+", delete=False) as temp_src:
        temp_src.write(sentence + "\n")
        temp_src_name = temp_src.name

    # --- Step 2: remove previous pred.txt if exists ---
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # --- Step 3: run OpenNMT ---
    cmd = [
        "onmt_translate",
        "--config", CONFIG_PATH,
        "--model", MODEL_PATH,
        "--src", temp_src_name,
        "--batch_size", "1"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"OpenNMT translation failed:\n{stderr}")

    # --- Step 4: read OpenNMT output from pred.txt ---
    if not os.path.exists(OUTPUT_FILE):
        raise FileNotFoundError(f"Expected output file '{OUTPUT_FILE}' not found.")

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        model_lines = [line.strip() for line in f.readlines() if line.strip()]

    model_output = model_lines[0] if model_lines else ""

    # --- Step 5: detokenize BPE in Python ---
    final_output = detokenize_bpe(model_output)

    # --- Step 6: cleanup temporary files ---
    os.remove(temp_src_name)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    return final_output

# --------- Main ---------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translate_text.py 'your sentence here'")
        sys.exit(1)

    input_text = sys.argv[1]
    final_translation = translate_cli(input_text)
    print(final_translation)

