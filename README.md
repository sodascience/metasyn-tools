# Metasyn apps/notebook with Marimo

This repository contains notebooks that can generate GMF files and convert GMF files to synthetic datasets.

Note that currently these notebooks and apps will give errors, since metasyn==2.x has dependencies that cannot be loaded into WASM. After metasyn 3.0 comes out these notebooks should be working.

## Apps

- `apps/create_synthetic.py`: Create synthetic data without an input dataset.
- `apps/convert_gmf.py`: Create a synthetic dataset from a GMF file.
