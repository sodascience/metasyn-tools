# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.25.0",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full", app_title="metasyn")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Metasyn - generate synthetic data
    """)
    return


@app.cell
async def _():
    import micropip

    await micropip.install("metasyn")
    import metasyn

    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from metasyn import MetaFrameBuilder
    from metasyn.registry import DistributionRegistry
    from metasyn.distribution import UniqueKeyDistribution, DiscreteTruncatedNormalDistribution, ColumnReference, IfThenElse

    return (
        ColumnReference,
        DiscreteTruncatedNormalDistribution,
        IfThenElse,
        MetaFrameBuilder,
        UniqueKeyDistribution,
        mo,
    )


@app.class_definition(hide_code=True)
class NoProgressBar():
    def update(self, val):
        pass
    def close(self):
        pass
    def set_description(self, desc):
        pass


@app.cell
def _(
    ColumnReference,
    DiscreteTruncatedNormalDistribution,
    IfThenElse,
    MetaFrameBuilder,
    UniqueKeyDistribution,
):
    builder = MetaFrameBuilder(n_rows=200)

    # Add 
    builder.add_column("PassengerId", var_type="discrete")
    builder["PassengerId"].distribution = UniqueKeyDistribution(1, True)

    # Add truncated normal distribution for age column
    builder.add_column("Age", var_type="discrete")
    builder["Age"].distribution = DiscreteTruncatedNormalDistribution(10, 80, 40, 10)

    # Add survival column that depends on the age of the passenger
    builder.add_column("Survived", var_type="string")
    builder["Survived"].distribution = IfThenElse(ColumnReference("Age") < 35, "Yes", "No")

    return (builder,)


@app.cell
def _(builder):
    mf = builder.fit(progress_bar=NoProgressBar())
    return (mf,)


@app.cell
def _(mf):
    df_syn = mf.synthesize(progress_bar=NoProgressBar())
    df_syn
    return (df_syn,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Generate a GMF file

    Below you can generate a GMF (Generative Metadata Format) file. This file can be used to generate synthetic data. You can also generate synthetic data immediately one paragraph below.
    """)
    return


@app.cell
def _(mf, mo):
    from metasyn.metaframe import _jsonify
    import json

    def _to_json(mf):
        mf_dict = _jsonify(mf.to_dict())
        return json.dumps(mf_dict, indent=4).encode("utf-8")


    mo.download(
        data=_to_json(mf),
        filename="gmf.json",
        mimetype="application/json",
        label="Generate GMF file"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Generate a CSV file

    With the button below you can download the CSV file with synthetic data.
    """)
    return


@app.cell
def _(df_syn, mf, mo):
    from metasyn.file import CsvFileInterface
    from io import BytesIO

    def _gen_csv(mf):
        handler = BytesIO()
        CsvFileInterface.default_interface("synthetic.csv").write_file(df_syn, handler)
    #    mf.write_synthetic(handler, file_format=CsvFileInterface.default_interface("synthetic.csv").to_dict(), progress_bar=False)
        return handler

    mo.download(
        data=_gen_csv(mf),
        filename="synthetic.csv",
        mimetype="text/csv",
        label="Generate CSV",
    )
    return


if __name__ == "__main__":
    app.run()
