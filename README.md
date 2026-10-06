# Metasyn apps/notebook with Marimo

This repository contains notebooks that can generate GMF files and convert GMF files to synthetic datasets.

## Apps

- `apps/create_synthetic.py`: Create synthetic data without an input dataset.
- `apps/convert_gmf.py`: Create a synthetic dataset from a GMF file. .SAV and .DTA are not supported, since pyreadstat is unsupported in pyodide.
